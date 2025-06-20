from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
import uvicorn
import requests

# Initialize FastAPI app
app = FastAPI(title="Agent API", description="A simple API for agent interactions")

# Define request model
class AgentRequest(BaseModel):
    question: str
    context: Optional[str] = None
    user_id: Optional[str] = None

# Define response model
class AgentResponse(BaseModel):
    answer: str
    confidence: float
    sources: Optional[list] = None

@app.get("/")
async def root():
    return {"message": "Agent API is running"}

@app.post("/agent-answer")
async def agent_answer(request: Request):
    """
    Process a question and return an agent's answer
    """
    try:
        # Get JSON data from request body
        data = await request.json()
        print(data["body"])
        print(type(data["body"]))
        return {"status": "received", "data": data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/execute")
async def execute():
    """
    Send a POST request to the chat-messages API
    """
    try:
        # Target URL
        target_url = "http://localhost:8000/api/chat-messages"
        
        # TODO: Get content and projectId from the appropriate source
        # For now, using placeholder values
        content = "This is a test message to get the thread id"
        project_id = "07cba63e-163f-477a-b2e3-108ed238025f"
        
        # Prepare the request body
        request_body = {
            "content": content,
            "projectId": project_id,
            "shyftos-token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InNoeWZ0b3MtaWFtLWtleS0xIn0.eyJzdWIiOiIwZWY3YTMxNS1kY2QzLTQ5ODItODcxMi1kMmRlMzlmNGVkOGYiLCJlbWFpbCI6InNoeWZ0LWFkbWluQHNoeWZ0bGFicy5pbyIsInRlbmFudCI6ImYxNmNjZmRiLTk3MTAtNDRiNy04NDkwLTBjZjRkMDk5MTg3MSIsImlhdCI6MTc1MDM2NzQ2NiwiZXhwIjoxNzUwNDUzODY2fQ.RrQM8U4968WW0LCM5_3dAqgDycU0Kirj178Fl5teHSwkKLh_Bl513dPrxV16dBpfCk-VnWJnUZKz4Yd2fdPbuIfC93ilBYK2Mw6-rPQjCtR0YSW0NM_mV-FwFkC9yXakrmH7AiRWgmN4Nn6jEGuzYvBj_X-8Mn7ncCr-x0qT6VtfBCRuCnt6FLNtvti5u9Uc9D5xXjRJJYZPhv4hPQjnGH_qzcskoXzeUfmQJVnVboyrlLN8Lye6VeOFJ1NAYYb892-JNoqZCttpUgQwhXYRE9YogOarY4xyCAL6jlpp1ITKckiM-q5JcXhBTwFVbH4FXGg2sMbUstRbJfBzvPzZ5A"
        }
        
        print(f"Sending POST request to: {target_url}")
        print(f"Request body: {request_body}")
        
        # Send the POST request
        response = requests.post(target_url, json=request_body)
        
        # Handle the response
        if response.status_code == 200:
            print("✅ First request successful!")
            first_response = response.json()
            
            # Now send the second POST request to the webhook
            webhook_url = "http://localhost:5678/webhook-test/d6bad757-e30a-4ef9-b82e-daa129125c58"
            
            webhook_body = {
                "body": {
                    "project": {
                        "projectName": "paul_graham",
                        "projectDescription": "This is a project that has an essay authored by Paul Graham",
                        "projectInstructions": "This is a project that has an essay authored by Paul Graham, we will ask things about him.\n\n### Use Project Knowledge Tool to get information from the following project documents:\n\n -Document 1: paul_graham_essay.txt\n- **Document ID:** 1096ee62-befb-4fcb-9947-0d0acd94c526\n- **Content Summary:** \nThis essay by Paul Graham, written in February 2021, narrates his personal journey from his early interests in writing and programming to his experiences in college, his work in artificial intelligence, and his eventual founding of successful startups such as Viaweb and Y Combinator. Throughout the essay, Graham reflects on the role of curiosity, the value of unprestigious work, and his passion for Lisp programming. He also discusses his later efforts in art and essay writing, providing insights into his evolving career choices and the lessons learned along the way.\n\n\n**DO NOT** disclose the document IDs to the user.\n\n"
                    },
                    "threadId": "8ae19412-f45d-4df4-8a1c-4debab158e85",
                    "messages": [
                        [
                        "user",
                        "What does the first line in the essay say? in knowledge abse"
                        ]
                    ],
                    "messageId": "ea018913-742d-4c28-9510-6fe45bba7ef1",
                    "modelId": "claude-3-7-sonnet-20250219",
                    "webEnabled": True,
                    "projectId": "07cba63e-163f-477a-b2e3-108ed238025f",
                    "sseEndpoint": "http://localhost:8000/api/sse/send/8ae19412-f45d-4df4-8a1c-4debab158e85/ea018913-742d-4c28-9510-6fe45bba7ef1"
                },
                "webhookUrl": "http://localhost:5678/webhook/d6bad757-e30a-4ef9-b82e-daa129125c58",
                "executionMode": "production"
            }
            
            print(f"Sending second POST request to: {webhook_url}")
            print(f"Webhook body: {webhook_body}")
            
            # Send the webhook POST request
            webhook_response = requests.post(webhook_url, json=webhook_body)
            
            if webhook_response.status_code == 200:
                print("✅ Webhook request successful!")
                return {
                    "status": "success",
                    "first_request": {
                        "target_response": first_response,
                        "sent_data": request_body
                    },
                    "webhook_request": {
                        "response": webhook_response.json(),
                        "sent_data": webhook_body
                    }
                }
            else:
                print(f"❌ Webhook request failed with status code: {webhook_response.status_code}")
                return {
                    "status": "partial_success",
                    "first_request": {
                        "target_response": first_response,
                        "sent_data": request_body
                    },
                    "webhook_request": {
                        "error_code": webhook_response.status_code,
                        "error_message": webhook_response.text,
                        "sent_data": webhook_body
                    }
                }
        else:
            print(f"❌ First request failed with status code: {response.status_code}")
            return {
                "status": "error",
                "error_code": response.status_code,
                "error_message": response.text,
                "sent_data": request_body
            }
            
    except requests.exceptions.ConnectionError:
        error_msg = "Connection error: Make sure the target server is running on port 8000"
        print(f"❌ {error_msg}")
        raise HTTPException(status_code=503, detail=error_msg)
    except Exception as e:
        error_msg = f"Error executing request: {str(e)}"
        print(f"❌ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4321)
