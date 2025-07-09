# navios-eval
evaluations from projects, chats, etc. RAG - Agents
run the FastAPI server and ping the  /execute endpoint to run the program

## Types of questions from the Dataset
Downloaded the first shard from the parquet files in the HF card: https://huggingface.co/datasets/lmms-lab/DocVQA 
|layout            |297|
|table/list        |253|
|free_text         |157|
|form              |150|
|figure/diagram    | 40|
|handwritten       | 32|
|Image/Photo       | 31|

# to RUN
(for the fastapi server)
python3 main.py

here's a sample request to the server:
curl -X GET "http://localhost:4321/execute?model=claude3.7&project_id=0ebede6b-e5a5-4a4f-8327-074aa285d81f&dataset=code&num_examples=20"

Where the project_id is the project that you create in your local instance of ShyftOS/NaviOS (you can get this from the URL)