import sys
import os

# Add the parent directory to sys.path to import from the backend package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from backend.agent import legal_agent
    
    print("Testing CourtAI Legal Agent...")
    
    queries = [
        "What is the punishment for murder?",
        "Someone cheated me and took my money",
        "Husband is treating wife with cruelty",
        "Threatening someone with injury"
    ]
    
    for q in queries:
        print(f"\nQuery: {q}")
        response = legal_agent.process_query(q)
        print(f"Answer: {response['answer']}")
        if response['sources']:
            print(f"Top Source: Section {response['sources'][0]['section']}")
        else:
            print("No sources found.")

except Exception as e:
    print(f"Error during testing: {e}")
