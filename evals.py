import json
from ragas import EvaluationDataset, evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import LLMContextPrecisionWithReference, LLMContextRecall, ResponseRelevancy, Faithfulness, FactualCorrectness, AnswerAccuracy
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import matplotlib.pyplot as plt
from datetime import datetime
import glob

# Helper function for descriptive filenames
def make_eval_filename(model, dataset, project_id, num_examples, suffix, attempt=None):
    date_str = datetime.now().strftime("%Y%m%d")
    base = f"{date_str}_{model}_{dataset}_proj-{project_id}_n{num_examples}"
    if attempt is not None:
        base = f"{base}_attempt{attempt:02d}"
    return f"{base}_{suffix}"

def run_ragas_evaluations(result_data, model, dataset, project_id, num_examples):
    """
    Run RAGAS evaluations on the provided result data
    Args:
        result_data (dict or list): The data to evaluate. Can be a single dictionary or a list of dictionaries.
        model (str): Model name
        dataset (str): Dataset name
        project_id (str): Project ID
        num_examples (int): Number of examples
    Returns:
        Evaluation result object or None if evaluation fails
    """
    try:
        # Ensure result_data is a list
        if isinstance(result_data, dict):
            dataset_list = [result_data]
        elif isinstance(result_data, list):
            dataset_list = result_data
        else:
            raise ValueError("result_data must be a dictionary or list of dictionaries")
        print(f"✅ Loaded dataset: {len(dataset_list)} entries")
        print(f"Dataset type: {type(dataset_list)}")
        # Show sample of the dataset structure
        if dataset_list:
            print(f"\n=== Sample Dataset Entry ===")
            sample_entry = dataset_list[0]
            for key, value in sample_entry.items():
                if key == 'retrieved_contexts' and isinstance(value, list):
                    print(f"  {key}: {len(value)} contexts")
                    if value:
                        first_context = value[0]
                        print(f"    First context: {first_context[:100]}..." if len(first_context) > 100 else f"    First context: {first_context}")
                elif isinstance(value, str) and len(value) > 100:
                    print(f"  {key}: {value[:100]}...")
                else:
                    print(f"  {key}: {value}")
        # Convert to RAGAS EvaluationDataset
        print(f"\n🔄 Converting to RAGAS EvaluationDataset...")
        evaluation_dataset = EvaluationDataset.from_list(dataset_list)
        print(f"✅ Successfully created EvaluationDataset")
        # Initialize the LLM
        print(f"\n🤖 Initializing LLM...")
        load_dotenv()
        OpenAI_key = os.getenv('OPENAI_API_KEY')
        llm = ChatOpenAI(model="gpt-4o", api_key=OpenAI_key)
        evaluator_llm = LangchainLLMWrapper(llm)
        print(f"✅ LLM initialized successfully")
        # Check if retrieved_contexts has meaningful content
        has_meaningful_contexts = False
        for example in dataset_list:
            if isinstance(example, dict) and 'retrieved_contexts' in example:
                contexts = example['retrieved_contexts']
                if isinstance(contexts, list):
                    if any(context and context.strip() for context in contexts):
                        print(f"✅ Found meaningful contexts in the dataset")
                        has_meaningful_contexts = True
                elif isinstance(contexts, str) and contexts.strip():
                    has_meaningful_contexts = True
        # Define metrics based on context availability
        if has_meaningful_contexts:
            metrics = [
                LLMContextPrecisionWithReference(),
                LLMContextRecall(),
                ResponseRelevancy(),
                Faithfulness(),
                FactualCorrectness(),
                AnswerAccuracy()
            ]
        else:
            metrics = [
                ResponseRelevancy(),
                FactualCorrectness(),
                AnswerAccuracy()
            ]
        # Run evaluations
        print(f"\n📊 Running RAGAS evaluations...")
        if has_meaningful_contexts:
            print(f"Metrics: LLMContextPrecisionWithReference, LLMContextRecall, ResponseRelevancy, Faithfulness, FactualCorrectness, AnswerAccuracy")
        else:
            print(f"Metrics: ResponseRelevancy, FactualCorrectness, AnswerAccuracy (context-based metrics skipped due to empty contexts)")
        result = evaluate(
            dataset=evaluation_dataset,
            metrics=metrics,
            llm=evaluator_llm
        )
        print(f"\n✅ Evaluations completed successfully!")  
        print(f"\n=== Evaluation Results ===")
        print(result)
        # Generate filename with date and attempt number
        current_date = datetime.now().strftime("%Y%m%d")
        # Count existing files for this date and parameters to determine attempt number
        pattern = f"./out_csvs/{current_date}_{model}_{dataset}_proj-{project_id}_n{num_examples}_attempt*_results.csv"
        existing_files = glob.glob(pattern)
        attempt_number = len(existing_files) + 1
        # Create filename prefix
        filename_prefix = make_eval_filename(model, dataset, project_id, num_examples, "results", attempt=attempt_number)
        # Save CSV results
        result.to_pandas().to_csv(f'./out_csvs/{filename_prefix}.csv')
        # Get available metrics from the results
        available_metrics = result.to_pandas().columns.tolist()
        # Create and save detailed metrics plot
        plot_metrics = []
        for metric in ['llm_context_precision_with_reference', 'context_recall',
                      'answer_relevancy', 'faithfulness', 'factual_correctness(mode=f1)',
                      'nv_accuracy']:
            if metric in available_metrics:
                plot_metrics.append(metric)
        if plot_metrics:
            data = result.to_pandas()[plot_metrics]
            ax = data.plot(kind='bar', figsize=(10, 6))
            plt.title('Evaluation Metrics Scores')
            plt.xticks(rotation=45, ha='right')
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            plt.savefig(f'./out_imgs/{filename_prefix}.png')
            plt.close()
            # Calculate and plot mean values for each metric
            mean_values = data.mean()
            plt.figure(figsize=(10, 6))
            ax = mean_values.plot(kind='bar')
            plt.title('Average Scores Across All Evaluation Metrics')
            plt.xticks(rotation=45, ha='right')
            for i, v in enumerate(mean_values):
                ax.text(i, v, f'{v:.2f}', ha='center', va='bottom')
            plt.tight_layout()
            agg_prefix = make_eval_filename(model, dataset, project_id, num_examples, "agg_results", attempt=attempt_number)
            plt.savefig(f'./out_imgs/{agg_prefix}.png')
            plt.close()
        else:
            print("No metrics available for plotting")
        return result
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you have the required packages installed:")
        print("pip install ragas langchain-openai")
        return None
    except Exception as e:
        print(f"❌ Error running evaluations: {e}")
        return None
