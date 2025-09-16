# on startup hit the IAM server /rbac/auth/login with user and password from env vars
# store the access_token
import os
from dotenv import load_dotenv
import requests
from sseclient import SSEClient
import json

def process_chat_query(content: str, project_id: str, model_id: str) -> dict:
    """
    Process a chat query and return the results
    
    Args:
        content (str): The message content to send
        project_id (str): The project ID to associate the message with
        model_id (str): The model ID to use for the query
        
    Returns:
        dict: The results containing retrieved_contexts and response
    """
    print(f"🚀 Starting process_chat_query with:")
    print(f"   Content: {content[:100]}{'...' if len(content) > 100 else ''}")
    print(f"   Project ID: {project_id}")
    print(f"   Model ID: {model_id}")
    
    # Load environment variables
    load_dotenv()

    # Get credentials from environment variables
    email = os.getenv('email')
    password = os.getenv('password')
    
    # Prepare login request
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }

    login_data = {
        "email": email,
        "password": password,
        "new_session": False
    }
    
    # Make login request
    print(f"🔐 Attempting login to local IAM service...")
    response = requests.post(
        "http://localhost:9009/rbac/auth/login",
        headers=headers,
        json=login_data,
    )

    if response.status_code == 200 or response.status_code == 201:
        access_token = response.json().get("access_token")
    else:
        print(f"Login request failed with status code: {response.status_code}")
        print(f"Login URL: http://localhost:9009/rbac/auth/login")
        print(f"Login data: {login_data}")
        print(f"Response body: {response.text}")
        raise Exception(f"Login failed with status code: {response.status_code}. Response: {response.text}")

    # Add header to all below requests -> "Authentication: Bearer {access_token}"
    def send_chat_message(content: str, project_id: str, modelId: str) -> dict:
        """
        Send a chat message to the API with authentication
        
        Args:
            content (str): The message content to send
            project_id (str): The project ID to associate the message with
            modelId (str): The model ID to use
            
        Returns:
            dict: The JSON response from the API
        """
        # Prepare the multipart form data
        form_data = {
            'content': (None, content),
            'projectId': (None, project_id),
            'modelId': (None, modelId)
        }

        # Set up headers with authentication
        headers = {
            'Authorization': f'Bearer {access_token}',
            'accept': '*/*'
        }

        # Make the POST request
        print(f"   🔍 Sending request with form data: {form_data}")
        response = requests.post(
            'http://localhost:9000/api/chat-messages',
            headers=headers,
            files=form_data
        )

        # Check if request was successful
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        
        else:
            print(f"Chat message request failed with status code: {response.status_code}")
            print(f"Request URL: http://localhost:9000/api/chat-messages")
            print(f"Request headers: {headers}")
            print(f"Request data: content={content}, projectId={project_id}, modelId={modelId}")
            print(f"Response body: {response.text}")
            raise Exception(f"Chat message request failed with status code: {response.status_code}. URL: http://localhost:9000/api/chat-messages, Response: {response.text}")

    # Send the chat message
    print(f"💬 Sending chat message to localhost:9000...")
    print(f"   Using model ID: {model_id}")
    print(f"   Request details: content='{content[:50]}...', projectId='{project_id}', modelId='{model_id}'")
    response = send_chat_message(content, project_id, model_id)
    
    print(f"📥 API Response: {response}")
    
    # Check if we can determine which model was actually used
    print(f"🔍 Checking response for model information...")
    if isinstance(response, list) and len(response) > 0:
        for msg in response:
            if msg.get('role') == 'assistant':
                print(f"   Assistant message ID: {msg.get('id')}")
                print(f"   Message format: {msg.get('format')}")
                print(f"   Content preview: {msg.get('content', '')[:100]}...")
                print(f"   Response style analysis:")
                content = msg.get('content', '')
                if '🚀' in content or '💬' in content or '📡' in content:
                    print(f"     - Contains emojis (likely Claude-style formatting)")
                if '##' in content or '###' in content:
                    print(f"     - Contains markdown headers (likely Claude-style formatting)")
                if 'Based on the' in content and len(content) > 500:
                    print(f"     - Long, detailed response (likely Claude-style)")
                if 'Here\'s how' in content or 'The calculator' in content:
                    print(f"     - Conversational tone (likely Claude-style)")
    
    # Extract assistant message ID from the response
    assistant_message_id = next((msg['id'] for msg in response if msg['role'] == 'assistant'), None)
    if not assistant_message_id:
        raise Exception("Could not find assistant message ID in response")

    # Connect to SSE stream
    print(f"📡 Connecting to SSE stream...")
    sse_url = f"http://localhost:9000/api/sse/connect/{assistant_message_id}"
    sse_response = requests.get(
        sse_url,
        headers={'Authorization': f'Bearer {access_token}', "accept": "*/*"},
        stream=True
    )
    
    if sse_response.status_code != 200:
        print(f"SSE connection failed with status code: {sse_response.status_code}")
        print(f"SSE URL: {sse_url}")
        print(f"SSE headers: {{'Authorization': f'Bearer {access_token[:20]}...', 'accept': '*/*'}}")
        print(f"SSE response body: {sse_response.text}")
        raise Exception(f"SSE connection failed with status code: {sse_response.status_code}. URL: {sse_url}, Response: {sse_response.text}")

    client = SSEClient(sse_response)

    # Initialize variables to store results
    retrieved_contexts = ""
    response_content = ""
    chunks = [""]
    response = "Wasn't able to retrieve any context or response"
    # Process SSE events
    import time
    last_event_time = time.time()
    timeout_seconds = 10  # 10 seconds timeout
    loop_start_time = time.time()
    max_loop_duration = 120  # 2 minutes in seconds
    
    for event in client.events():
        current_time = time.time()
        
        # Check if we've been waiting too long for events
        if current_time - last_event_time > timeout_seconds:
            print("⏰ No events received for 10 seconds, breaking loop")
            break
            
        # Check if the entire loop has been running for more than 2 minutes
        if current_time - loop_start_time > max_loop_duration:
            print("⏰ SSE loop has been running for more than 2 minutes, breaking loop")
            break
            
        last_event_time = current_time
        
        data = json.loads(event.data)
        if data["done"] == True:
            # returns the final message as a string
            final_message = data['chunk']['finalMessage']['content']
            if "</ToolCall>" in final_message:
                response = final_message.split("</ToolCall>")[-1].strip()
            else:
                response = final_message
            break
        elif data["chunk"]["event"] == "toolResult":
            # returns an array with the chunks
            tool_content = data['chunk']['chunk']['tools']['messages'][0]['kwargs']['content']
            # Parse the list structure and extract only the "text" values
            try:
                if isinstance(tool_content, str):
                    # If it's a string, try to parse it as JSON
                    tool_content = json.loads(tool_content)
                
                if isinstance(tool_content, list):
                    # Extract only the "text" values from each object
                    chunks = [json.loads(item.get("text", {})).get("pageContent", "") for item in tool_content if isinstance(item, dict) and "text" in item]
                else:
                    chunks = [tool_content]
            except (json.JSONDecodeError, TypeError):
                # If parsing fails, keep the original content
                chunks = [tool_content]
            #print(f"Chunks: {chunks}")
    print("Retreived Contexts: ", len(chunks))

    # Prepare results
    results = {
        "response": response,
        "retrieved_contexts": chunks
    }
    print("<query>")
    print(content)
    print("</query>")
    print("<response>")
    print(results["response"])
    print("</response>")
    
    return results
