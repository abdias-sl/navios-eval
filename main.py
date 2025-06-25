from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
import uvicorn
import requests
import json
from evals import run_ragas_evaluations
from get_data import process_chat_query

# Initialize FastAPI app
app = FastAPI(title="Agent API", description="A simple API for agent interactions")

@app.get("/")
async def root():
    return {"message": "Agent API is running"}

@app.get("/execute")
async def execute():
    try:
        # Call process_chat_query with example parameters
        # Load and process first 5 records from rag_dataset.json
        with open('./datasets/essay/rag_dataset.json', 'r') as f:
            dataset = json.load(f)
            
        results = []
        model = "gpt-4o"
        for example in dataset['examples'][:10]:
            query = example['query']
            reference = example['reference_answer']
            
            result = process_chat_query(
                content=query,
                project_id="07cba63e-163f-477a-b2e3-108ed238025f",
                model_id=model
            )
            results.append({
                'user_input': query,
                'retrieved_contexts': result["retrieved_contexts"],
                'response': result["response"],
                'reference': reference
            })
        # Run RAGAS evaluations on results
        evaluation_results = run_ragas_evaluations(results, model)
        print("evaluation_results")
        return {"message": "Execution complete", "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing query: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4321)
