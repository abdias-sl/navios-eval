import pandas as pd
import json
from ragas import EvaluationDataset, evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import ResponseRelevancy, FactualCorrectness, AnswerAccuracy
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import matplotlib.pyplot as plt
from datetime import datetime
import glob

def prepare_evaluation_dataset(df, response_column):
    """
    Prepare dataset for evaluation from a specific response column
    
    Args:
        df (DataFrame): The consolidated dataframe
        response_column (str): The response column to use
        
    Returns:
        list: List of dictionaries ready for evaluation
    """
    evaluation_data = []
    
    for _, row in df.iterrows():
        evaluation_data.append({
            "user_input": row['query'],
            "response": row[response_column],
            "reference": row['reference']
        })
    
    return evaluation_data

def run_comparison_evaluations():
    """
    Read consolidated CSV, evaluate all response columns, and create comparison plots
    """
    try:
        # Load the consolidated dataset
        print("📊 Loading consolidated dataset...")
        df = pd.read_csv('./datasets/consolidated.csv')
        
        # Cast all columns to strings to handle NaN values
        df = df.astype(str)
        
        # Strip trailing and leading spaces from all string values
        for column in df.columns:
            df[column] = df[column].str.strip()
        
        print(f"✅ Loaded dataset with {len(df)} rows")
        print(f"Columns: {list(df.columns)}")
        
        # Define response columns to evaluate
        response_columns = [
            'response_default',
            'response_thinking', 
            'response_c37',
            'response_c35',
            'response_gpt'
        ]
        
        # Filter to only include columns that exist in the dataframe
        available_columns = [col for col in response_columns if col in df.columns]
        print(f"📋 Available response columns: {available_columns}")
        
        if not available_columns:
            raise ValueError("No response columns found in the dataset")
        
        # Initialize the LLM
        print(f"\n🤖 Initializing LLM...")
        load_dotenv()
        OpenAI_key = os.getenv('OPENAI_API_KEY')
        llm = ChatOpenAI(model="gpt-4o", api_key=OpenAI_key)
        evaluator_llm = LangchainLLMWrapper(llm)
        print(f"✅ LLM initialized successfully")
        
        # Define metrics
        metrics = [
            ResponseRelevancy(),
            FactualCorrectness(),
            AnswerAccuracy()
        ]
        
        print(f"\n📊 Running evaluations for {len(available_columns)} response columns...")
        print(f"Metrics: ResponseRelevancy, FactualCorrectness, AnswerAccuracy")
        
        # Store all results
        all_results = {}
        
        # Evaluate each response column
        for response_col in available_columns:
            print(f"\n🔄 Evaluating {response_col}...")
            
            # Prepare dataset for this response column
            evaluation_data = prepare_evaluation_dataset(df, response_col)
            
            # Convert to RAGAS EvaluationDataset
            evaluation_dataset = EvaluationDataset.from_list(evaluation_data)
            
            # Run evaluation
            result = evaluate(
                dataset=evaluation_dataset,
                metrics=metrics,
                llm=evaluator_llm
            )
            
            all_results[response_col] = result
            print(f"✅ Completed evaluation for {response_col}")
        
        # Generate filename with date and attempt number
        current_date = datetime.now().strftime("%Y%m%d")
        pattern = f"./out_csvs/{current_date}_*_comparison.csv"
        existing_files = glob.glob(pattern)
        attempt_number = len(existing_files) + 1
        filename_prefix = f"{current_date}_attempt{attempt_number:02d}"
        
        # Save individual CSV results
        for response_col, result in all_results.items():
            csv_filename = f'./out_csvs/{filename_prefix}_{response_col}_comparison.csv'
            result.to_pandas().to_csv(csv_filename)
            print(f"💾 Saved {response_col} results to {csv_filename}")
        
        # Create comparison plots
        print(f"\n📈 Creating comparison plots...")
        
        # Prepare data for comparison
        comparison_data = {}
        for response_col, result in all_results.items():
            df_result = result.to_pandas()
            # Calculate mean scores for each metric
            comparison_data[response_col] = {
                'ResponseRelevancy': df_result['answer_relevancy'].mean(),
                'FactualCorrectness': df_result['factual_correctness(mode=f1)'].mean(),
                'AnswerAccuracy': df_result['nv_accuracy'].mean()
            }
        
        # Create comparison dataframe
        comparison_df = pd.DataFrame(comparison_data).T
        
        # Plot 1: Bar chart comparing all models across all metrics
        plt.figure(figsize=(12, 8))
        comparison_df.plot(kind='bar', figsize=(12, 8))
        plt.title('Model Comparison Across All Metrics')
        plt.xlabel('Response Column')
        plt.ylabel('Score')
        plt.xticks(rotation=45, ha='right')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(f'./out_imgs/{filename_prefix}_comparison_all_metrics.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Plot 2: Individual metric comparisons
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        metrics_names = ['ResponseRelevancy', 'FactualCorrectness', 'AnswerAccuracy']
        
        for i, metric in enumerate(metrics_names):
            axes[i].bar(comparison_df.index, comparison_df[metric])
            axes[i].set_title(f'{metric} Comparison')
            axes[i].set_ylabel('Score')
            axes[i].tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for j, v in enumerate(comparison_df[metric]):
                axes[i].text(j, v, f'{v:.3f}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(f'./out_imgs/{filename_prefix}_comparison_individual_metrics.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Plot 3: Heatmap style comparison
        plt.figure(figsize=(10, 6))
        plt.imshow(comparison_df.T, cmap='YlOrRd', aspect='auto')
        plt.colorbar(label='Score')
        plt.xticks(range(len(comparison_df.index)), comparison_df.index, rotation=45, ha='right')
        plt.yticks(range(len(comparison_df.columns)), comparison_df.columns)
        plt.title('Model Performance Heatmap')
        
        # Add text annotations
        for i in range(len(comparison_df.columns)):
            for j in range(len(comparison_df.index)):
                plt.text(j, i, f'{comparison_df.iloc[j, i]:.3f}', 
                        ha='center', va='center', color='black', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(f'./out_imgs/{filename_prefix}_comparison_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Save comparison summary
        comparison_summary = {
            'date': current_date,
            'attempt': attempt_number,
            'total_examples': len(df),
            'response_columns_evaluated': available_columns,
            'metrics_used': ['ResponseRelevancy', 'FactualCorrectness', 'AnswerAccuracy'],
            'results': comparison_data
        }
        
        with open(f'./out_csvs/{filename_prefix}_comparison_summary.json', 'w') as f:
            json.dump(comparison_summary, f, indent=2)
        
        print(f"\n✅ Comparison evaluation completed successfully!")
        print(f"📊 Results saved with prefix: {filename_prefix}")
        print(f"📈 Generated comparison plots:")
        print(f"   - {filename_prefix}_comparison_all_metrics.png")
        print(f"   - {filename_prefix}_comparison_individual_metrics.png") 
        print(f"   - {filename_prefix}_comparison_heatmap.png")
        
        return comparison_data
        
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        return None
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you have the required packages installed:")
        print("pip install ragas langchain-openai pandas matplotlib")
        return None
    except Exception as e:
        print(f"❌ Error running comparison evaluations: {e}")
        return None

if __name__ == "__main__":
    print("=== Model Comparison Evaluations ===")
    comparison_results = run_comparison_evaluations()
    
    if comparison_results:
        print(f"\n✅ Comparison completed successfully!")
        print(f"Results summary:")
        for model, scores in comparison_results.items():
            print(f"  {model}:")
            for metric, score in scores.items():
                print(f"    {metric}: {score:.3f}")
    else:
        print(f"\n❌ Comparison failed!")
