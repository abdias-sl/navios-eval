import json
from ragas import EvaluationDataset, evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import LLMContextPrecisionWithReference, LLMContextRecall, ResponseRelevancy, Faithfulness, FactualCorrectness, AnswerAccuracy
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

def run_ragas_evaluations(result_data, filename):
    """
    Run RAGAS evaluations on the provided result data
    
    Args:
        result_data (dict or list): The data to evaluate. Can be a single dictionary or a list of dictionaries.
        
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
        
        # Run evaluations
        print(f"\n📊 Running RAGAS evaluations...")
        print(f"Metrics: LLMContextPrecisionWithReference, LLMContextRecall, ResponseRelevancy, Faithfulness, FactualCorrectness, AnswerAccuracy")
        
        result = evaluate(
            dataset=evaluation_dataset,
            metrics=[LLMContextPrecisionWithReference(),
                     LLMContextRecall(),
                     ResponseRelevancy(),
                     Faithfulness(),
                     FactualCorrectness(),
                     AnswerAccuracy()],
            llm=evaluator_llm
        )
        
        print(f"\n✅ Evaluations completed successfully!")  
        print(f"\n=== Evaluation Results ===")
        print(result)
        import matplotlib.pyplot as plt
        result.to_pandas().to_csv(f'./out_csvs/evaluation_results_{filename}.csv')
        data = result.to_pandas()[['llm_context_precision_with_reference', 'context_recall',
        'answer_relevancy', 'faithfulness', 'factual_correctness(mode=f1)',
        'nv_accuracy']]
        ax = data.plot(kind='bar', figsize=(10, 6))
        plt.title('Evaluation Metrics Scores')
        plt.xticks(rotation=45, ha='right')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
        plt.tight_layout()
        plt.savefig(f'./out_imgs/evaluation_results_{filename}.png')
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
        plt.savefig(f'./out_imgs/agg_evaluation_results_{filename}.png')
        
        return result
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you have the required packages installed:")
        print("pip install ragas langchain-openai")
        return None
    except Exception as e:
        print(f"❌ Error running evaluations: {e}")
        return None
