import requests
import json

def test_agent_answer():
    # Server URL
    url = "http://localhost:4321/agent-answer"
    
    # Test data - you can modify this to test different payloads
    test_data = {
        "question": "What is the weather like today?",
        "user_id": "test_user_123",
        "context": "Weather inquiry",
        "timestamp": "2024-01-15T10:30:00Z"
    }
    
    try:
        # Send POST request
        print("Sending POST request to:", url)
        print("Data:", json.dumps(test_data, indent=2))
        
        response = requests.post(url, json=test_data)
        
        # Print response details
        print(f"\nResponse Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Request successful!")
            print("Response Body:")
            print(json.dumps(response.json(), indent=2))
        else:
            print("❌ Request failed!")
            print("Response Body:", response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the FastAPI server is running on port 4321")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_agent_answer() 