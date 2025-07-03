from fastapi import FastAPI, HTTPException, Request, Query
from pydantic import BaseModel
from typing import Optional
import uvicorn
import requests
import json
from evals import run_ragas_evaluations
from get_data import process_chat_query

# Initialize FastAPI app
app = FastAPI(title="Agent API", description="A simple API for agent interactions")

# Dataset filepath mappings
DATASET_PATHS = {
    "code": "./datasets/code/code_examples.json",
    "docs": "./datasets/docVQA/selected_examples.json",
    "single": "./datasets/essay/rag_dataset.json"
}

# Model mappings
MODEL_MAPPINGS = {
    "claude3.7": "claude-3-7-sonnet-20250219",
    "claude3.5": "claude-3-5-sonnet-20241022", 
    "gpt4o": "gpt-4o"
}

@app.get("/")
async def root():
    return {"message": "Agent API is running"}

@app.get("/execute")
async def execute(
    model: str = Query(..., description="Model to use: claude3.7, claude3.5, or gpt4o"),
    project_id: str = Query(..., description="Project ID for the query"),
    dataset: str = Query(..., description="Dataset to use: code, docs, or single"),
    num_examples: int = Query(10, description="Number of examples to process (default: 10)")
):
    try:
        # Validate model parameter
        if model not in MODEL_MAPPINGS:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid model. Must be one of: {list(MODEL_MAPPINGS.keys())}"
            )
        
        # Validate dataset parameter
        if dataset not in DATASET_PATHS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid dataset. Must be one of: {list(DATASET_PATHS.keys())}"
            )
        
        # Validate num_examples parameter
        if num_examples <= 0:
            raise HTTPException(
                status_code=400,
                detail="num_examples must be greater than 0"
            )
        
        # Get the actual model ID and dataset path
        actual_model_id = MODEL_MAPPINGS[model]
        dataset_path = DATASET_PATHS[dataset]
        
        # Load and process dataset
        try:
            with open(dataset_path, 'r') as f:
                dataset_data = json.load(f)
        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail=f"Dataset file not found: {dataset_path}"
            )
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid JSON format in dataset file: {dataset_path}"
            )
        
        # Get the actual number of examples available
        total_examples = len(dataset_data['examples'])
        
        # Adjust num_examples if it exceeds the available examples
        actual_num_examples = min(num_examples, total_examples)
        
        if num_examples > total_examples:
            print(f"Warning: Requested {num_examples} examples but only {total_examples} available. Using {actual_num_examples} examples.")
            
        results = []
        for example in dataset_data['examples'][:actual_num_examples]:
            query = example['query']
            reference = example['reference_answer']
            
            result = process_chat_query(
                content=query,
                project_id=project_id,
                model_id=actual_model_id
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
        
        return {
            "message": "Execution complete", 
            "status": "success",
            "model": model,
            "project_id": project_id,
            "dataset": dataset,
            "requested_examples": num_examples,
            "total_available_examples": total_examples,
            "actual_processed_examples": actual_num_examples,
            "results_count": len(results)
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing query: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=4321)
