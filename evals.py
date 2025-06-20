import json
from ragas import EvaluationDataset, evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import LLMContextPrecisionWithReference, LLMContextRecall, ResponseRelevancy, Faithfulness, FactualCorrectness, AnswerAccuracy
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

def run_ragas_evaluations():
    """
    Load final.json and run RAGAS evaluations
    """
    try:
        # Load the final dataset
        final_file_path = './datasets/out/final.json'
        with open(final_file_path, 'r') as f:
            dataset = json.load(f)
        
        print(f"✅ Loaded final dataset: {len(dataset)} entries")
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
        
        return result
        
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        return None
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you have the required packages installed:")
        print("pip install ragas langchain-openai")
        return None
    except Exception as e:
        print(f"❌ Error running evaluations: {e}")
        return None

if __name__ == "__main__":
    print("=== RAGAS Evaluations ===")
    evaluation_results = run_ragas_evaluations()
    
    if evaluation_results:
        print(f"\n✅ Evaluations completed successfully!")
        print(f"Results saved in memory")
    else:
        print(f"\n❌ Evaluations failed!")
