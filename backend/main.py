import PyPDF2
import fitz  # PyMuPDF
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load .env from project root (two levels up from this file)
_root = os.path.join(os.path.dirname(__file__), '..')
load_dotenv(os.path.join(_root, '.env'))

try:
    from .agent import legal_agent
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from agent import legal_agent


app = Flask(__name__, static_folder='../courtai', static_url_path='/')
CORS(app)  # Enable CORS for all routes

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/status')
def status():
    return "CourtAI Backend is Running! Access the app at http://127.0.0.1:8000/"

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({"error": "Missing 'query' in request body"}), 400
    
    query = data['query']
    language = data.get('language', 'en')  # Default to English
    
    try:
        response_data = legal_agent.process_query(query, lang=language)
        return jsonify(response_data)
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({"error": "An internal error occurred while processing your request"}), 500

@app.route('/analyze_fir', methods=['POST'])
def analyze_fir():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    language = request.form.get('language', 'en')
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    text = ""
    try:
        file_bytes = file.read()
        content_type = file.content_type
        
        if content_type.startswith('image/'):
            # Process as image (Vision)
            analysis_data = legal_agent.analyze_image(file_bytes, lang=language)
        else:
            # Process as PDF/Text
            text = ""
            if file.filename.endswith('.pdf'):
                doc = fitz.open(stream=file_bytes, filetype="pdf")
                for page in doc:
                    text += page.get_text()
            else:
                text = file_bytes.decode('utf-8')
                
            if not text.strip():
                return jsonify({"error": "Could not extract text from the document"}), 400
                
            analysis_data = legal_agent.analyze_document(text, lang=language)
            
        return jsonify(analysis_data)
        
    except Exception as e:
        print(f"FIR Analysis Error: {e}")
        return jsonify({"error": f"Error processing FIR: {str(e)}"}), 500

@app.route('/nearby_help', methods=['POST'])
def nearby_help():
    data = request.get_json()
    lat = data.get('lat')
    lon = data.get('lon')
    
    # In a real app, we'd use a Places API. 
    # For this professional demo, we synthesize a realistic response.
    maps_link = f"https://www.google.com/maps/search/police+station/@{lat},{lon},15z"
    
    return jsonify({
        "station": "Nearest Police Station (Based on your location)",
        "helpline": "NALSA (Legal Aid): 15100",
        "emergency": "Police: 100 / 112",
        "maps_url": maps_link
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
