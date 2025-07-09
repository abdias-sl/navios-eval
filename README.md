# navios-eval

**navios-eval** is a framework for evaluating large language models (LLMs) and agent-based systems on a variety of tasks, including code understanding, document question answering (DocVQA), essay analysis, and more. It supports retrieval-augmented generation (RAG) and agent workflows, and provides tools for dataset management, evaluation, and result visualization.

## Features

- **FastAPI Server**: Exposes endpoints for running model evaluations and health checks.
- **Multi-Task Evaluation**: Supports code, document, and essay datasets.
- **Flexible Model Support**: Easily switch between models (e.g., Claude 3.7, Claude 3.5, GPT-4o).
- **Automated Metrics**: Uses RAGAS and other metrics for relevance, factuality, and accuracy.
- **Visualization**: Generates comparison plots and summary statistics.
- **Extensible Datasets**: Easily add new datasets for different domains.

## Project Structure

```
navios-eval/
  ├── main.py                # FastAPI server and main entry point
  ├── evals.py               # RAGAS and other evaluation logic
  ├── comparison.py          # Model comparison and visualization
  ├── get_data.py            # Data fetching and chat query processing
  ├── datasets/              # All datasets (code, docVQA, essays, etc.)
  ├── out_csvs/              # Output CSVs for results and comparisons
  ├── out_imgs/              # Output images for plots and visualizations
  ├── requirements.txt       # Python dependencies
  └── README.md              # Project documentation
```

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/navios-eval.git
   cd navios-eval
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Create a `.env` file with your credentials and API keys (see `.env.example` if available).
   - Required variables: `email`, `password`, `OPENAI_API_KEY`, etc.

## Usage

### Running the FastAPI Server

Start the server:
```bash
python main.py
```

The server will be available at `http://localhost:4321`.

### Example API Request

To run an evaluation, use the `/execute` endpoint:

```bash
curl -X GET "http://localhost:4321/execute?model=claude3.7&project_id=YOUR_PROJECT_ID&dataset=code&num_examples=20"
```

- `model`: One of `claude3.7`, `claude3.5`, or `gpt4o`
- `project_id`: Your project ID from ShyftOS/NaviOS
- `dataset`: One of `code`, `docs`, or `single`
- `num_examples`: Number of examples to process

### Health Check

```bash
curl http://localhost:4321/health
```

## Datasets

- **Code**: QA pairs for code understanding (e.g., Ethereum wallet, task manager).
- **DocVQA**: Document question answering, with images and structured questions.
- **Essay**: RAG-based essay datasets for open-ended evaluation.

Example dataset breakdown (DocVQA):
| Type             | Count |
|------------------|-------|
| layout           | 297   |
| table/list       | 253   |
| free_text        | 157   |
| form             | 150   |
| figure/diagram   | 40    |
| handwritten      | 32    |
| Image/Photo      | 31    |

## Output

- **CSV files**: Results and comparison metrics are saved in `out_csvs/`.
- **Images**: Plots and visualizations are saved in `out_imgs/`.

## Extending the Project

- Add new datasets to the `datasets/` directory and update `DATASET_PATHS` in `main.py`.
- Add new models to `MODEL_MAPPINGS` in `main.py`.
- Implement new evaluation metrics in `evals.py` or `comparison.py`.
