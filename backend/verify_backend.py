import requests
import json
import time
import subprocess
import os
import signal

def test_analyze_fir():
    print("\nTesting /analyze_fir endpoint...")
    url = "http://127.0.0.1:8000/analyze_fir"
    
    # Create a dummy text file for testing (since we can't easily create a PDF here without libraries)
    test_file_path = "test_fir.txt"
    with open(test_file_path, "w") as f:
        f.write("FIR Copy: The accused person threatened the victim with a weapon at Andheri station. Section 506 and 323 are applicable.")
    
    try:
        with open(test_file_path, "rb") as f:
            files = {'file': (test_file_path, f, 'text/plain')}
            data = {'lang': 'en'}
            response = requests.post(url, files=files, data=data, timeout=30)
            
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("\n--- FIR Analysis Response ---")
            print(f"Summary: {data.get('summary')[:100]}...")
            print(f"Sections found: {[s.get('section') for s in data.get('sections', [])]}")
            print(f"Guidance: {data.get('guidance')[:100]}...")
            print("-----------------------------\n")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"FIR Analysis test failed: {e}")
        return False
    finally:
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_all():
    print("Starting CourtAI Backend Verification...")
    # Start the Flask server in a separate process
    process = subprocess.Popen(
        ["python", "backend/main.py"],
        cwd=os.getcwd(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Wait for server to start
    print("Waiting for server to initialize (15s)...")
    time.sleep(15) 

    try:
        # Test /ask
        print("\nTesting /ask endpoint...")
        url = "http://127.0.0.1:8000/ask"
        payload = {"query": "Someone is threatening me"}
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            print("[SUCCESS] /ask endpoint is working.")
        else:
            print(f"[FAILED] /ask endpoint: {response.status_code}")

        # Test /analyze_fir
        if test_analyze_fir():
            print("[SUCCESS] /analyze_fir endpoint is working.")
        else:
            print("[FAILED] /analyze_fir endpoint.")

    except Exception as e:
        print(f"Verification encountered an error: {e}")
    finally:
        print("Stopping server...")
        if os.name == 'nt':
            subprocess.call(['taskkill', '/F', '/T', '/PID', str(process.pid)])
        else:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)

if __name__ == "__main__":
    test_all()
