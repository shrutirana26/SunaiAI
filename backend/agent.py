import os
from google import genai
from google.genai import types
try:
    from .retriever import retriever
except ImportError:
    from retriever import retriever
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure Gemini client
client = None
if GOOGLE_API_KEY:
    client = genai.Client(api_key=GOOGLE_API_KEY)
    print("[OK] Google Gemini AI connected successfully.")
else:
    print("[WARNING] GOOGLE_API_KEY not found. AI explanations will be simulated.")

MODEL_ID = "gemini-2.0-flash"

def generate_text(prompt: str) -> str:
    """Simple text generation wrapper."""
    if not client:
        return ""
    response = client.models.generate_content(model=MODEL_ID, contents=prompt)
    return response.text

def generate_vision(prompt: str, image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    """Vision (image+text) generation wrapper."""
    if not client:
        return ""
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            prompt
        ]
    )
    return response.text


class LegalAgent:
    def __init__(self):
        self.retriever = retriever
        self.severity_map = {
            "302": {"risk": "High",   "bail": "Non-Bailable", "seriousness": "Critical"},
            "307": {"risk": "High",   "bail": "Non-Bailable", "seriousness": "Critical"},
            "376": {"risk": "High",   "bail": "Non-Bailable", "seriousness": "Critical"},
            "392": {"risk": "High",   "bail": "Non-Bailable", "seriousness": "High"},
            "420": {"risk": "Medium", "bail": "Non-Bailable", "seriousness": "Moderate"},
            "379": {"risk": "Medium", "bail": "Bailable",     "seriousness": "Moderate"},
            "323": {"risk": "Low",    "bail": "Bailable",     "seriousness": "Low"},
            "504": {"risk": "Low",    "bail": "Bailable",     "seriousness": "Low"},
            "506": {"risk": "Medium", "bail": "Bailable",     "seriousness": "Moderate"},
        }

    # ─────────────────────────────────────────────
    # Analytics helpers
    # ─────────────────────────────────────────────
    def get_analysis_metadata(self, sections):
        risk = "Low"; bail = "Bailable"; seriousness = "Low"
        for s in sections:
            meta = self.severity_map.get(s['section'], {"risk": "Low", "bail": "Bailable", "seriousness": "Low"})
            if meta['risk'] == "High": risk = "High"
            elif meta['risk'] == "Medium" and risk != "High": risk = "Medium"
            if meta['bail'] == "Non-Bailable": bail = "Non-Bailable"
            if meta['seriousness'] == "Critical": seriousness = "Critical"
            elif meta['seriousness'] == "High" and seriousness != "Critical": seriousness = "High"
            elif meta['seriousness'] == "Moderate" and seriousness not in ["Critical", "High"]: seriousness = "Moderate"
        return {
            "risk_level": risk,
            "bail_status": bail,
            "seriousness": seriousness,
            "risk_score": 85 if risk == "High" else (45 if risk == "Medium" else 15),
            "confidence": 92 if client else 75
        }

    def generate_timeline(self, metadata):
        return [
            {"title": "FIR Filed",      "desc": "Initial document recorded by police for cognizable offense."},
            {"title": "Investigation",  "desc": "Police gather evidence, record statements, and identify accused."},
            {"title": "Chargesheet",    "desc": "Official formal accusation filed in court after investigation."},
            {"title": "Trial",          "desc": "Court proceedings where evidence is presented and argued."},
            {"title": "Judgment",       "desc": "Final decision by the magistrate/judge on the case."}
        ]

    # ─────────────────────────────────────────────
    # Language helpers
    # ─────────────────────────────────────────────
    def _lang_name(self, lang):
        return {'en': 'English', 'hi': 'Hindi (हिंदी)', 'mr': 'Marathi (मराठी)'}.get(lang, 'English')

    def _translate_sections(self, sections, lang):
        if lang == 'en' or not client:
            return sections
        target_lang = self._lang_name(lang)
        translated = []
        for s in sections:
            prompt = (
                f"Translate the following legal section title and description into {target_lang}. "
                f"Keep the Section number as is.\nTitle: {s['title']}\nDescription: {s['description']}\n\n"
                f"Output only the translated Title and Description separated by a pipe (|)."
            )
            try:
                text = generate_text(prompt)
                parts = text.split('|')
                translated.append({
                    "section": s['section'],
                    "title": parts[0].strip() if parts else s['title'],
                    "description": parts[1].strip() if len(parts) > 1 else s['description']
                })
            except Exception:
                translated.append(s)
        return translated

    # ─────────────────────────────────────────────
    # Core generation methods
    # ─────────────────────────────────────────────
    def explain_law(self, sections, query, lang='en'):
        if not client:
            return self._simulate_explanation(sections, query, lang)
        target_lang = self._lang_name(lang)
        context = "\n\n".join([f"Section {s['section']} - {s['title']}: {s['description']}" for s in sections])
        prompt = (
            f"You are a helpful Indian Legal Assistant.\n"
            f"User Query: \"{query}\"\n\n"
            f"Relevant IPC Sections:\n{context}\n\n"
            f"Task: Provide a simple, empathetic explanation of how these laws apply to the user's situation.\n"
            f"- IMPORTANT: Your entire response MUST be in {target_lang}.\n"
            f"- Use simple language suitable for a common person.\n"
            f"- Mention the specific section numbers.\n"
            f"- Keep it concise but informative."
        )
        try:
            return generate_text(prompt)
        except Exception as e:
            print(f"explain_law error: {e}")
            return self._simulate_explanation(sections, query, lang)

    def generate_guidance(self, sections, query, lang='en'):
        if not client:
            return "Consult a legal professional immediately.\nDocument all evidence.\nVisit the nearest police station if necessary."
        target_lang = self._lang_name(lang)
        section_ids = ", ".join([s['section'] for s in sections])
        prompt = (
            f"User Situation: \"{query}\"\nRelevant IPC Sections: {section_ids}\n\n"
            f"Task: Provide clear, actionable guidance in {target_lang}.\n"
            f"1. What you can do next (practical immediate actions).\n"
            f"2. When to file a complaint.\n"
            f"3. Where to go (police, cyber cell, women's cell, etc).\n"
            f"- Be simple and empathetic. Use words like 'suggested' or 'consider'.\n"
            f"- Ensure the output is entirely in {target_lang}."
        )
        try:
            return generate_text(prompt)
        except Exception as e:
            print(f"generate_guidance error: {e}")
            return "Consult a lawyer.\nStay safe."

    def _simulate_explanation(self, sections, query, lang='en'):
        top = sections[0] if sections else {"section": "N/A", "title": "Unknown", "description": ""}
        if lang == 'hi':
            return (f"आपकी क्वेरी के आधार पर, सबसे प्रासंगिक कानूनी प्रावधान **IPC धारा {top['section']}** "
                    f"({top['title']}) है।\n\n**कानून क्या कहता है:** {top['description']}")
        elif lang == 'mr':
            return (f"तुमच्या क्वेरीवर आधारित, सर्वात संबंधित कायदेशीर तरतूद **IPC कलम {top['section']}** "
                    f"({top['title']}) आहे.\n\n**कायदा काय सांगतो:** {top['description']}")
        return (f"Based on your query, the most relevant legal provision is **IPC Section {top['section']}** "
                f"({top['title']}).\n\n**What the law says:** {top['description']}")

    # ─────────────────────────────────────────────
    # Image / OCR analysis
    # ─────────────────────────────────────────────
    def analyze_image(self, image_bytes, lang='en'):
        if not client:
            return {"error": "AI Vision model not available. Please set GOOGLE_API_KEY in your .env file."}
        target_lang = self._lang_name(lang)
        prompt = (
            f"Analyze this image which is an FIR or a legal document.\n"
            f"1. Perform high-accuracy OCR to extract the incident details and sections.\n"
            f"2. Provide a clear summary in {target_lang}.\n"
            f"3. Identify any IPC/BNS sections mentioned.\n"
            f"4. Provide guidance in {target_lang}."
        )
        try:
            llm_text = generate_vision(prompt, image_bytes)
            sections = self.retriever.retrieve_law(llm_text[:1000], top_k=3)
            translated = self._translate_sections(sections, lang)
            metadata = self.get_analysis_metadata(sections)
            for s in translated:
                s['bailable'] = self.severity_map.get(s['section'], {}).get('bail') != "Non-Bailable"
            return {
                "bail_status": metadata.get("bail_status", "Unknown"),
                "risk_level": metadata.get("risk_level", "Unknown"),
                "sections": translated,
                "sections_count": len(translated),
                "legal_findings": llm_text,
                "ai_summary": llm_text.split('\n')[0] if '\n' in llm_text else llm_text,
                "recommendations": self.generate_guidance(sections, llm_text[:500], lang),
                "nearby_help": [
                    {"type": "Police", "name": "Nearest Police Station", "contact": "100 / 112"},
                    {"type": "Legal Aid", "name": "NALSA Helpline", "contact": "15100"}
                ]
            }
        except Exception as e:
            print(f"analyze_image error: {e}")
            return {"error": f"Failed to analyze image: {str(e)}"}

    # ─────────────────────────────────────────────
    # Document / PDF analysis
    # ─────────────────────────────────────────────
    def analyze_document(self, text, lang='en'):
        target_lang = self._lang_name(lang)
        if not client:
            sections = self.retriever.retrieve_law(text[:1000], top_k=3)
            return {
                "bail_status": "Unknown",
                "risk_level": "Unknown",
                "sections": sections,
                "sections_count": len(sections),
                "legal_findings": self._simulate_explanation(sections, "Document Analysis", lang),
                "ai_summary": "Summary: The document describes a potential legal incident. (Simulation)",
                "recommendations": "Consult a legal professional immediately.",
                "nearby_help": [
                    {"type": "Police", "name": "Nearest Police Station", "contact": "100 / 112"},
                    {"type": "Legal Aid", "name": "NALSA Helpline", "contact": "15100"}
                ]
            }
        prompt = (
            f"You are an expert Indian Legal Analyzer.\n"
            f"Analyzing the following document (FIR/Legal Text):\n\n\"{text[:6000]}\"\n\n"
            f"Task:\n"
            f"1. Provide a clear, factual summary of the incident in {target_lang}.\n"
            f"2. Identify the core legal issues.\n"
            f"3. Keep the tone professional and objective.\n\n"
            f"Output: Just the summary and analysis text."
        )
        try:
            summary = generate_text(prompt)
            sections = self.retriever.retrieve_law(text[:2000], top_k=3)
            translated = self._translate_sections(sections, lang)
            explanation = self.explain_law(sections, "Explain the legal sections found in this document.", lang)
            guidance = self.generate_guidance(sections, text[:1000], lang)
            metadata = self.get_analysis_metadata(sections)
            for s in translated:
                s['bailable'] = self.severity_map.get(s['section'], {}).get('bail') != "Non-Bailable"
            return {
                "bail_status": metadata.get("bail_status", "Unknown"),
                "risk_level": metadata.get("risk_level", "Unknown"),
                "sections": translated,
                "sections_count": len(translated),
                "legal_findings": explanation,
                "ai_summary": summary,
                "recommendations": guidance,
                "nearby_help": [
                    {"type": "Police", "name": "Nearest Police Station", "contact": "100 / 112"},
                    {"type": "Legal Aid", "name": "NALSA Helpline", "contact": "15100"}
                ]
            }
        except Exception as e:
            print(f"analyze_document error: {e}")
            return {"error": "Failed to analyze document."}

    # ─────────────────────────────────────────────
    # Q&A / Chat query
    # ─────────────────────────────────────────────
    def process_query(self, user_query, lang='en'):
        target_lang = self._lang_name(lang)
        summary = ""

        # Summarize long text
        if len(user_query) > 500 and client:
            try:
                summary = generate_text(
                    f"Provide a brief, factual summary of this legal incident in {target_lang}:\n\n{user_query[:4000]}"
                )
            except Exception as e:
                print(f"Summarization error: {e}")

        retrieval_query = summary if summary else user_query
        sections = self.retriever.retrieve_law(retrieval_query)
        translated = self._translate_sections(sections, lang)

        if not sections:
            no_result = {
                'en': "I'm sorry, I couldn't find any specific IPC sections matching your query.",
                'hi': "क्षमा करें, मुझे कोई विशिष्ट IPC धारा नहीं मिली।",
                'mr': "क्षमस्व, मला कोणतेही विशिष्ट IPC कलम आढळले नाही."
            }
            answer = no_result.get(lang, no_result['en'])
            guidance_bullets = ""
        else:
            answer = self.explain_law(sections, user_query, lang)
            guidance_bullets = self.generate_guidance(sections, user_query, lang)

        disclaimers = {
            'en': "\n\n---\n⚠️ **Disclaimer:** This is not legal advice. Call NALSA at 15100 for help.",
            'hi': "\n\n---\n⚠️ **अस्वीकरण:** यह कानूनी सलाह नहीं है। NALSA को 15100 पर कॉल करें।",
            'mr': "\n\n---\n⚠️ **अस्वीकरण:** हा कायदेशीर सल्ला नाही. NALSA ला 15100 वर कॉल करा।"
        }

        metadata = self.get_analysis_metadata(sections) if sections else None
        timeline = self.generate_timeline(metadata) if sections else []
        for s in translated:
            s['bailable'] = self.severity_map.get(s['section'], {}).get('bail') != "Non-Bailable"
        if metadata:
            metadata['bail_type'] = "Regular/Anticipatory (Strict Conditions)" if metadata['risk_level'] == "High" else "Regular Bail"

        return {
            "answer": answer + disclaimers.get(lang, disclaimers['en']),
            "guidance": guidance_bullets,
            "sources": translated,
            "sections": translated,
            "summary": summary if summary else "Direct user query processed.",
            "metadata": metadata,
            "timeline": timeline
        }


# Singleton instance
legal_agent = LegalAgent()
