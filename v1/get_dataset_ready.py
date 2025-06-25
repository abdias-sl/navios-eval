import json
import os
from typing import List, Dict, Any

def create_final_dataset():
    """
    Load formatted_answers.json and consolidated_dataset.json to create final dataset
    """
    try:
        # Load the formatted answers
        answers_file_path = './datasets/out/formatted_answers.json'
        with open(answers_file_path, 'r') as f:
            formatted_answers = json.load(f)
        
        print(f"✅ Loaded formatted answers: {len(formatted_answers)} entries")
        print(f"Answers type: {type(formatted_answers)}")
        
        # Load the consolidated dataset
        consolidated_file_path = './datasets/out/consolidated_dataset.json'
        with open(consolidated_file_path, 'r') as f:
            consolidated_data = json.load(f)
        
        print(f"✅ Loaded consolidated dataset: {len(consolidated_data)} entries")
        print(f"Consolidated data type: {type(consolidated_data)}")
        
        # Create empty dataset array
        dataset = []
        
        # Process first 10 entries (data is already in order)
        for i in range(min(10, len(consolidated_data))):
            consolidated_entry = consolidated_data[i]
            
            # Extract data from consolidated entry
            csv_data = consolidated_entry.get('csv_data', {})
            rag_data = consolidated_entry.get('rag_data', {})
            
            # Get the required fields
            user_input = rag_data.get('query', '')
            retrieved_contexts = csv_data.get('content', [])
            reference = rag_data.get('reference_answer', '')
            
            # Get response from formatted answers (assuming same order)
            # We'll use the first 10 entries from formatted answers
            if i < len(formatted_answers):
                # Get the first key-value pair from formatted answers
                answers_list = list(formatted_answers.items())
                if i < len(answers_list):
                    thread_id, response = answers_list[i]
                else:
                    response = ''
            else:
                response = ''
            
            # Create the dataset object
            dataset_entry = {
                "user_input": user_input,
                "retrieved_contexts": retrieved_contexts,
                "response": response,
                "reference": reference
            }
            
            dataset.append(dataset_entry)
            
            # Show sample of first entry
            if i == 0:
                print(f"\n=== Sample Dataset Entry {i+1} ===")
                print(f"user_input: {user_input[:100]}..." if len(user_input) > 100 else f"user_input: {user_input}")
                print(f"retrieved_contexts: {len(retrieved_contexts)} items")
                if retrieved_contexts:
                    first_context = retrieved_contexts[0]
                    print(f"  First context: {first_context[:100]}..." if len(first_context) > 100 else f"  First context: {first_context}")
                print(f"response: {response[:100]}..." if len(response) > 100 else f"response: {response}")
                print(f"reference: {reference[:100]}..." if len(reference) > 100 else f"reference: {reference}")
        
        print(f"\n✅ Created dataset with {len(dataset)} entries")
        
        # Create output directory if it doesn't exist
        output_dir = './datasets/out'
        os.makedirs(output_dir, exist_ok=True)
        
        # Save to final.json
        output_path = os.path.join(output_dir, 'final.json')
        with open(output_path, 'w') as f:
            json.dump(dataset, f, indent=2)
        
        print(f"💾 Saved final dataset to: {output_path}")
        
        # Show file size
        if os.path.exists(output_path):
            size = os.path.getsize(output_path)
            print(f"📊 File size: {size:,} bytes")
        
        # Show summary statistics
        print(f"\n=== Summary ===")
        print(f"Formatted answers loaded: {len(formatted_answers)}")
        print(f"Consolidated data loaded: {len(consolidated_data)}")
        print(f"Final dataset entries: {len(dataset)}")
        
        return dataset
        
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error creating final dataset: {e}")
        return None

if __name__ == "__main__":
    print("=== Final Dataset Creation ===")
    final_dataset = create_final_dataset()
    
    if final_dataset:
        print(f"\n✅ Dataset creation successful!")
        print(f"Final dataset has {len(final_dataset)} entries")
    else:
        print(f"\n❌ Dataset creation failed!")
