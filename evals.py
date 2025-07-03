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

def run_ragas_evaluations(result_data, filename):
    """
    Run RAGAS evaluations on the provided result data
    
    Args:
        result_data (dict or list): The data to evaluate. Can be a single dictionary or a list of dictionaries.
        filename (str): The filename parameter to append to the saved files.
        
    Returns:
        Evaluation result object or None if evaluation fails
    """
    try:
        # Ensure result_data is a list
        if isinstance(result_data, dict):
            dataset = [result_data]
        elif isinstance(result_data, list):
            dataset = result_data
        else:
            raise ValueError("result_data must be a dictionary or list of dictionaries")
        
        print(f"✅ Loaded dataset: {len(dataset)} entries")
        print(f"Dataset type: {type(dataset)}")
        
        # Show sample of the dataset structure
        if dataset:
            print(f"\n=== Sample Dataset Entry ===")
            sample_entry = dataset[0]
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
        evaluation_dataset = EvaluationDataset.from_list(dataset)
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
        for example in result_data:
            if isinstance(example, dict) and 'retrieved_contexts' in example:
                contexts = example['retrieved_contexts']
                if isinstance(contexts, list):
                    # Check if any context is not empty
                    if any(context and context.strip() for context in contexts):
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
        
        # Count existing files for this date and filename to determine attempt number
        pattern = f"./out_csvs/{current_date}_*_{filename}.csv"
        existing_files = glob.glob(pattern)
        attempt_number = len(existing_files) + 1
        
        # Create filename prefix
        filename_prefix = f"{current_date}_attempt{attempt_number:02d}"
        
        # Save CSV results
        result.to_pandas().to_csv(f'./out_csvs/{filename_prefix}_{filename}.csv')
        
        # Get available metrics from the results
        available_metrics = result.to_pandas().columns.tolist()
        
        # Create and save detailed metrics plot
        # Only include metrics that are actually present in the results
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
            plt.savefig(f'./out_imgs/{filename_prefix}_{filename}.png')
            plt.close()
            
            # Calculate and plot mean values for each metric
            mean_values = data.mean()
            plt.figure(figsize=(10, 6))
            ax = mean_values.plot(kind='bar')
            plt.title('Average Scores Across All Evaluation Metrics')
            plt.xticks(rotation=45, ha='right')
            
            # Add value labels on top of each bar
            for i, v in enumerate(mean_values):
                ax.text(i, v, f'{v:.2f}', ha='center', va='bottom')
                
            plt.tight_layout()
            plt.savefig(f'./out_imgs/{filename_prefix}_agg_{filename}.png')
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
