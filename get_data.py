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
    response = requests.post(
        "http://localhost:9009/rbac/auth/login",
        headers=headers,
        json=login_data,
    )

    if response.status_code == 200 or response.status_code == 201:
        access_token = response.json().get("access_token")
    else:
        raise Exception(f"Login failed with status code: {response.status_code}")

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
        response = requests.post(
            'http://localhost:9000/api/chat-messages',
            headers=headers,
            files=form_data
        )

        # Check if request was successful
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        
        else:
            raise Exception(f"Chat message request failed with status code: {response.status_code}")

    # Send the chat message
    response = send_chat_message(content, project_id, model_id)
    
    # Extract assistant message ID from the response
    assistant_message_id = next((msg['id'] for msg in response if msg['role'] == 'assistant'), None)
    if not assistant_message_id:
        raise Exception("Could not find assistant message ID in response")

    # Connect to SSE stream
    sse_url = f"http://localhost:9000/api/sse/connect/{assistant_message_id}"
    sse_response = requests.get(
        sse_url,
        headers={'Authorization': f'Bearer {access_token}', "accept": "*/*"},
        stream=True
    )

    client = SSEClient(sse_response)

    # Process SSE events
    chunks = [""]
    response = "Wasn't able to retrieve any context or response"
    for event in client.events():
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
    
    return results
