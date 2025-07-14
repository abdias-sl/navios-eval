import json
import pandas as pd
import os

def parse_final_qas():
    """
    Parse final_qas.json and extract reference_answer values
    """
    # File path
    json_file = "./datasets/final_qas.json"
    
    # Check if file exists
    if not os.path.exists(json_file):
        print(f"❌ File not found: {json_file}")
        return
    
    print(f"📖 Reading file: {json_file}")
    
    try:
        # Read the JSON file
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Successfully read JSON file")
        
        # Extract reference_answer values
        references = []
        
        # Check if data is a list or has a specific structure
        if isinstance(data, list):
            # If it's a list of objects
            for item in data:
                if isinstance(item, dict) and 'reference_answer' in item:
                    references.append(item['reference_answer'])
        elif isinstance(data, dict):
            # If it's a dictionary with a specific structure
            if 'examples' in data:
                # Structure like {"examples": [{"reference_answer": "..."}, ...]}
                for example in data['examples']:
                    if isinstance(example, dict) and 'reference_answer' in example:
                        references.append(example['reference_answer'])
            else:
                # Check if it has reference_answer directly
                if 'reference_answer' in data:
                    references.append(data['reference_answer'])
        
        print(f"📊 Found {len(references)} reference answers")
        
        if not references:
            print("❌ No reference_answer values found in the file")
            print("Available keys in data:", list(data.keys()) if isinstance(data, dict) else "Data is a list")
            return
        
        # Clean up the references (remove extra whitespace)
        cleaned_references = []
        for i, reference in enumerate(references, 1):
            # Remove leading/trailing whitespace and normalize
            cleaned_reference = str(reference).strip()
            cleaned_references.append(cleaned_reference)
            print(f"📝 Reference {i}: {cleaned_reference[:100]}..." if len(cleaned_reference) > 100 else f"📝 Reference {i}: {cleaned_reference}")
        
        # Create DataFrame
        df = pd.DataFrame({
            'reference': cleaned_references
        })
        
        # Save to CSV
        output_file = "./reference_answers.csv"
        df.to_csv(output_file, index=False)
        
        print(f"\n✅ Successfully parsed {len(cleaned_references)} reference answers")
        print(f"💾 Saved to: {output_file}")
        print(f"📊 DataFrame shape: {df.shape}")
        
        # Show first few rows
        print(f"\n📋 First few references:")
        print(df.head())
        
        return df
        
    except json.JSONDecodeError as e:
        print(f"❌ Error decoding JSON: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ Error parsing file: {str(e)}")
        return None

def main():
    """
    Main function to run the parsing
    """
    print("=== Final QAs Parser ===")
    df = parse_final_qas()
    
    if df is not None:
        print(f"\n✅ Parsing completed successfully!")
        print(f"📊 Total reference answers extracted: {len(df)}")
    else:
        print(f"\n❌ Parsing failed!")

if __name__ == "__main__":
    main()
