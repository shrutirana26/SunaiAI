let selectedLanguage = 'en';
const API_BASE_URL = '';
let gaugeChart = null;
let trendChart = null;

// Navigation Logic
function navigateTo(screenId, navEl) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById(`screen-${screenId}`).classList.add('active');
    
    if (navEl) {
        document.querySelectorAll('.nav-link').forEach(n => n.classList.remove('active'));
        navEl.classList.add('active');
    }
}

// Open Live Camera
let cameraStream = null;
async function openCamera(navEl) {
    if (navEl) {
        document.querySelectorAll('.nav-link').forEach(n => n.classList.remove('active'));
        navEl.classList.add('active');
    }
    navigateTo('camera');
    try {
        cameraStream = await navigator.mediaDevices.getUserMedia({ 
            video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } } 
        });
        const video = document.getElementById('webcam');
        video.srcObject = cameraStream;
    } catch (err) {
        console.error('Camera Error:', err);
        alert('Could not access camera.');
        navigateTo('dashboard');
    }
}

function stopCamera() {
    if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
        cameraStream = null;
    }
    navigateTo('dashboard');
}

async function captureSnapshot() {
    const video = document.getElementById('webcam');
    const canvas = document.getElementById('snapshot-canvas') || document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    stopCamera();
    canvas.toBlob(blob => processFile(blob, 'scan.jpg'), 'image/jpeg', 0.9);
}

// Upload/Process FIR
async function uploadFIR(input) {
    if (!input.files || input.files.length === 0) return;
    processFile(input.files[0], input.files[0].name);
}

async function processFile(file, filename) {
    showLoading(true);
    const formData = new FormData();
    formData.append('file', file, filename);
    formData.append('language', selectedLanguage);

    try {
        const response = await fetch(`/analyze_fir`, { method: 'POST', body: formData });
        const data = await response.json();
        displayResults(data);
    } catch (err) {
        console.error('Upload Error:', err);
        alert('Analysis failed.');
        showLoading(false);
    }
}

async function askAI() {
    const input = document.getElementById('ai-query');
    const query = input.value.trim();
    if (!query) return;

    showLoading(true);
    try {
        const response = await fetch(`/ask`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, language: selectedLanguage })
        });
        const data = await response.json();
        displayResults(data);
        input.value = '';
    } catch (err) {
        console.error('Ask AI Error:', err);
        alert('Query failed.');
        showLoading(false);
    }
}

// Analytics Charts
function initCharts() {
    const gaugeCtx = document.getElementById('gauge-chart');
    if (gaugeCtx && !gaugeChart) {
        gaugeChart = new Chart(gaugeCtx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [0, 100],
                    backgroundColor: ['#3b82f6', 'rgba(255,255,255,0.05)'],
                    borderWidth: 0,
                    circumference: 360,
                    rotation: 0,
                    cutout: '85%',
                    borderRadius: 10
                }]
            },
            options: { cutout: '85%', plugins: { tooltip: { enabled: false }, legend: { display: false } } }
        });
    }

    const trendCtx = document.getElementById('trend-chart');
    if (trendCtx && !trendChart) {
        trendChart = new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
                datasets: [{
                    label: 'Risk Trend',
                    data: [10, 25, 45, 30, 50],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 2,
                    pointRadius: 0
                }]
            },
            options: {
                plugins: { legend: { display: false } },
                scales: {
                    x: { display: false },
                    y: { display: false }
                }
            }
        });
    }
}

function updateCharts(meta) {
    if (!gaugeChart || !trendChart) initCharts();
    
    if (meta && gaugeChart) {
        const score = meta.risk_score || 0;
        const color = meta.risk_level === 'High' ? '#ef4444' : (meta.risk_level === 'Medium' ? '#f59e0b' : '#10b981');
        
        gaugeChart.data.datasets[0].data = [score, 100 - score];
        gaugeChart.data.datasets[0].backgroundColor[0] = color;
        gaugeChart.update();
        document.getElementById('gauge-label').innerText = score + '%';
        document.getElementById('gauge-label').style.color = color;

        // Simulate a trend line movement based on current risk
        trendChart.data.datasets[0].data.push(score);
        trendChart.data.datasets[0].data.shift();
        trendChart.data.datasets[0].borderColor = color;
        trendChart.update();
    }
}

// Result Rendering
function displayResults(data) {
    try {
        console.log('Displaying Results:', data);
        initCharts();
        const center = document.getElementById('result-center-display');
        center.innerHTML = '';

        // Add Legal Cards
        const sections = data.sections || data.sources || [];
        sections.forEach(s => {
            const card = document.createElement('div');
            card.className = `legal-card ${s.bailable === false ? 'danger' : 'success'}`;
            card.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="font-weight: 800; font-size: 14px; margin-bottom: 4px;">Section ${s.section}</div>
                    <span style="font-size: 10px; font-weight: 800; opacity: 0.8;">${s.bailable === false ? 'NON-BAILABLE' : 'BAILABLE'}</span>
                </div>
                <div style="font-size: 16px; font-weight: 700; margin-bottom: 8px; font-family: var(--font-outfit);">${s.title}</div>
                <div style="font-size: 13px; color: var(--text-muted); line-height: 1.5;">${s.description}</div>
            `;
            center.appendChild(card);
        });

        // Add Timeline
        if (data.timeline) {
            const tlWrap = document.createElement('div');
            tlWrap.style.marginTop = '40px';
            tlWrap.innerHTML = '<h3 style="font-family: var(--font-outfit); font-size: 20px; margin-bottom: 24px;">Case Roadmap</h3>';
            const timeline = document.createElement('div');
            timeline.className = 'timeline';
            data.timeline.forEach(step => {
                const item = document.createElement('div');
                item.className = 'timeline-step';
                item.innerHTML = `<div style="font-weight: 700; font-size: 14px;">${step.title}</div><div style="font-size: 12px; color: var(--text-muted);">${step.desc}</div>`;
                timeline.appendChild(item);
            });
            tlWrap.appendChild(timeline);
            center.appendChild(tlWrap);
        }

        // 2. Center Content - Explanation (Answer)
        const resultDisplay = document.getElementById('result');
        if (data.legal_findings) {
            resultDisplay.innerHTML = `<div style="margin-top: 32px; padding-top: 24px; border-top: 1px solid var(--border); font-size: 15px; line-height: 1.7; color: var(--text-main); font-family: var(--font-outfit);">
                <div style="font-size: 12px; font-weight: 800; color: var(--accent); margin-bottom: 12px; text-transform: uppercase;">Legal Findings</div>
                ${window.marked ? marked.parse(data.legal_findings) : data.legal_findings}
            </div>`;
        } else {
            resultDisplay.innerHTML = '';
        }

        // 3. Right Panel (Analytics & Summary)
        const summaryText = data.ai_summary || data.summary || 'No summary available.';
        document.getElementById('case-summary-box').innerHTML = window.marked ? marked.parse(summaryText) : summaryText;
        
        const analytics = document.getElementById('analytics-grid');
        analytics.innerHTML = '';
        
        // Ensure Top Stats are at least visible as N/A
        const bailStat = document.getElementById('stat-bail');
        const riskStat = document.getElementById('stat-risk');
        const countStat = document.getElementById('stat-count');

        const bailStatus = data.bail_status || (data.metadata ? data.metadata.bail_status : 'Unknown');
        const riskLevel = data.risk_level || (data.metadata ? data.metadata.risk_level : 'Unknown');
        const riskScore = riskLevel === 'High' ? 85 : (riskLevel === 'Medium' ? 45 : 15);

        const stats = [
            { label: 'Bail Prediction', val: bailStatus, color: riskLevel === 'High' ? 'var(--danger)' : 'var(--success)' },
            { label: 'Risk Score', val: riskScore + '/100', color: '#fff' }
        ];
        stats.forEach(s => {
            analytics.innerHTML += `
                <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border); padding: 16px; border-radius: var(--radius-md);">
                    <div style="font-size: 10px; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">${s.label}</div>
                    <div style="font-size: 16px; font-weight: 800; color: ${s.color}; margin-top: 4px;">${s.val}</div>
                </div>
            `;
        });

        // Update Top Stats Quick View
        bailStat.innerText = bailStatus;
        riskStat.innerText = riskLevel;
        riskStat.style.color = riskLevel === 'High' ? 'var(--danger)' : (riskLevel === 'Medium' ? '#f59e0b' : 'var(--success)');
        
        // Update Visual Charts
        updateCharts({ risk_level: riskLevel, risk_score: riskScore });
        
        countStat.innerText = data.sections_count || sections.length;

        // Guidance
        const guidance = document.getElementById('guidance-display');
        const recs = data.recommendations || data.guidance;
        if (recs) {
            guidance.innerHTML = `<div style="font-size: 14px; line-height: 1.6; color: var(--text-muted);">
                ${window.marked ? marked.parse(recs) : recs}
            </div>`;
        } else {
            guidance.innerHTML = '';
        }

        // 4. Nearby Help (Right Column)
        const helpContainer = document.getElementById('nearby-help-display');
        helpContainer.innerHTML = '';
        const helpData = data.nearby_help || (data.help_data ? [data.help_data] : null);
        if (helpData && helpData.length > 0) {
            let helpHtml = `<div style="background: rgba(236, 72, 153, 0.05); border: 1px solid rgba(236, 72, 153, 0.2); border-left: 4px solid #ec4899; padding: 20px; border-radius: var(--radius-md); margin-top: 24px;">
                <div style="font-size: 10px; font-weight: 800; color: #ec4899; margin-bottom: 12px; text-transform: uppercase;">Nearby Assistance</div>`;
            helpData.forEach(h => {
                helpHtml += `<div style="font-weight: 700; font-size: 14px; margin-bottom: 4px; color: #fff;">${h.name || h.station || 'Assistance'}</div>
                <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 16px;">Contact: ${h.contact || h.helpline || 'N/A'}</div>`;
                if (h.maps_url) {
                    helpHtml += `<a href="${h.maps_url}" target="_blank" class="btn-glass" style="padding: 8px 16px; font-size: 11px; width: 100%; justify-content: center;">
                        <span class="material-icons-round" style="font-size: 14px;">map</span> View Location
                    </a>`;
                }
            });
            helpHtml += `</div>`;
            helpContainer.innerHTML = helpHtml;
        }

        showLoading(false);
        navigateTo('results');
    } catch (err) {
        console.error('Display Error:', err);
        showLoading(false);
    }
}

async function findNearbyHelp(navEl) {
    if (navEl) {
        document.querySelectorAll('.nav-link').forEach(n => n.classList.remove('active'));
        navEl.classList.add('active');
    }
    showLoading(true);
    navigator.geolocation.getCurrentPosition(async (pos) => {
        try {
            const response = await fetch(`/nearby_help`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ lat: pos.coords.latitude, lon: pos.coords.longitude })
            });
            const data = await response.json();
            displayResults({ help_data: data });
        } catch (err) { alert('Help failed.'); showLoading(false); }
    }, () => { alert('Geo access denied.'); showLoading(false); });
}

function showLoading(show) {
    document.getElementById('loading-overlay').classList.toggle('active', show);
}

const UI_TRANSLATIONS = {
    en: {
        'nav-overview': 'Overview', 'nav-analyzer': 'FIR Analyzer', 'nav-scan': 'Scan Document', 'nav-help': 'Nearby Help',
        'hero-title': 'Legal Intelligence <span style="color: var(--accent)">Dashboard</span>',
        'hero-sub': 'Advanced FIR analysis and legal rights monitoring for professional aid.',
        'label-bail': 'Bail Status', 'label-risk': 'Risk Level', 'label-count': 'Sections Count',
        'user-role': 'Advocate AI', 'user-tier': 'Pro Version', 'lang-btn': 'Switch to Hindi'
    },
    hi: {
        'nav-overview': 'अवलोकन', 'nav-analyzer': 'FIR विश्लेषक', 'nav-scan': 'दस्तावेज़ स्कैन करें', 'nav-help': 'नज़दीकी सहायता',
        'hero-title': 'कानूनी इंटेलिजेंस <span style="color: var(--accent)">डैशबोर्ड</span>',
        'hero-sub': 'पेशेवर सहायता के लिए उन्नत FIR विश्लेषण और कानूनी अधिकार निगरानी।',
        'label-bail': 'जमानत की स्थिति', 'label-risk': 'जोखिम स्तर', 'label-count': 'धाराओं की संख्या',
        'user-role': 'अधिवक्ता AI', 'user-tier': 'प्रो संस्करण', 'lang-btn': 'Switch to Marathi'
    },
    mr: {
        'nav-overview': 'आढावा', 'nav-analyzer': 'FIR विश्लेषक', 'nav-scan': 'दस्तऐवज स्कॅन करा', 'nav-help': 'जवळपासची मदत',
        'hero-title': 'कायदेशीर इंटेलिजेंस <span style="color: var(--accent)">डॅशबोर्ड</span>',
        'hero-sub': 'व्यावसायिक मदतीसाठी प्रगत FIR विश्लेषण आणि कायदेशीर अधिकार देखरेख.',
        'label-bail': 'जामीन स्थिती', 'label-risk': 'धोक्याची पातळी', 'label-count': 'कलमांची संख्या',
        'user-role': 'अधिवक्ता AI', 'user-tier': 'प्रो आवृत्ती', 'lang-btn': 'Switch to English'
    }
};

function applyUITranslations() {
    const t = UI_TRANSLATIONS[selectedLanguage];
    for (const id in t) {
        const el = document.getElementById(id);
        if (el) {
            if (id === 'lang-btn') {
                el.innerHTML = `<span class="material-icons-round">language</span> ${t[id]}`;
            } else {
                el.innerHTML = t[id];
            }
        }
    }
}

function toggleLang() {
    if (selectedLanguage === 'en') selectedLanguage = 'hi';
    else if (selectedLanguage === 'hi') selectedLanguage = 'mr';
    else selectedLanguage = 'en';
    
    applyUITranslations();
}
