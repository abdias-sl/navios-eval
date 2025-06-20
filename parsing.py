import pandas as pd
import json
from typing import List, Dict, Any
import os

def load_and_filter_json():
    """
    Load JSON file and filter to keep only specific keys from examples array
    """
    try:
        # Load the JSON file
        with open('./datasets/essay/rag_dataset.json', 'r') as file:
            data = json.load(file)
        
        print(f"JSON loaded successfully")
        print(f"Data type: {type(data)}")
        
        if isinstance(data, dict):
            print(f"Top-level keys: {list(data.keys())}")
        
        # Find the examples array
        examples = None
        if isinstance(data, dict) and 'examples' in data:
            examples = data['examples']
        elif isinstance(data, list):
            examples = data
        
        if examples is None:
            print("Error: Could not find examples array in JSON")
            return None
        
        print(f"Found examples array with {len(examples)} items")
        
        # Filter each example to keep only specified keys
        filtered_examples = []
        for i, example in enumerate(examples):
            if isinstance(example, dict):
                filtered_example = {}
                
                # Keep only the specified keys if they exist
                if 'query' in example:
                    filtered_example['query'] = example['query']
                if 'reference_contexts' in example:
                    filtered_example['reference_contexts'] = example['reference_contexts']
                if 'reference_answer' in example:
                    filtered_example['reference_answer'] = example['reference_answer']
                
                filtered_examples.append(filtered_example)
            else:
                print(f"Warning: Example {i} is not a dictionary, skipping")
        
        print(f"Filtered to {len(filtered_examples)} examples")
        
        # Show sample of filtered data
        if filtered_examples:
            print("\n=== Sample Filtered Examples ===")
            for i, example in enumerate(filtered_examples[:3]):  # Show first 3
                print(f"\nExample {i + 1}:")
                for key, value in example.items():
                    if key == 'reference_contexts' and isinstance(value, list):
                        print(f"  {key}: {len(value)} contexts")
                    elif key == 'reference_answer' and isinstance(value, str):
                        print(f"  {key}: {value[:100]}..." if len(value) > 100 else f"  {key}: {value}")
                    else:
                        print(f"  {key}: {value}")
        
        return filtered_examples
        
    except FileNotFoundError:
        print("Error: JSON file not found at './datasets/essay/rag_dataset.json'")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return None

def read_and_parse_csv():
    """
    Read CSV file and parse payload column as JSON
    """
    try:
        # Read the CSV file
        df = pd.read_csv('./datasets/first_ten_qs.csv')
        
        print(f"CSV loaded successfully. Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print("\nFirst few rows (before sorting):")
        print(df.head())
        
        # Sort by created_at column in ascending order
        df_sorted = df.sort_values('created_at', ascending=True)
        
        print(f"\nAfter sorting by created_at (ascending):")
        print(df_sorted.head())
        
        # Parse the payload column (string JSON to Python dict)
        parsed_data = []
        
        for index, row in df_sorted.iterrows():
            try:
                # Parse the JSON string in payload column
                payload_dict = json.loads(row['payload'])
                
                parsed_data.append({
                    'id': row['id'],
                    'payload': payload_dict
                })
                
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON at row {index}: {e}")
                print(f"Payload string: {row['payload']}")
                continue
        
        print(f"\nSuccessfully parsed {len(parsed_data)} rows")
        
        # Group by ID to find pairs
        id_groups = {}
        for item in parsed_data:
            id_val = item['id']
            if id_val not in id_groups:
                id_groups[id_val] = []
            id_groups[id_val].append(item['payload'])
        
        # Display paired data
        print("\n=== Paired Data by ID (sorted by created_at) ===")
        for id_val, payloads in id_groups.items():
            print(f"\nID: {id_val}")
            print(f"Number of payloads: {len(payloads)}")
            for i, payload in enumerate(payloads, 1):
                print(f"  Payload {i}:")
                print(f"    Type: {type(payload)}")
                print(f"    Keys: {list(payload.keys()) if isinstance(payload, dict) else 'Not a dict'}")
                if isinstance(payload, dict):
                    # Print first few key-value pairs for preview
                    for key, value in list(payload.items())[:3]:
                        print(f"    {key}: {value}")
                print()
        
        return parsed_data, id_groups
        
    except FileNotFoundError:
        print("Error: CSV file not found at './datasets/first_ten_qs.csv'")
        return None, None
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None, None

if __name__ == "__main__":
    # Create output directory if it doesn't exist
    output_dir = './datasets/out'
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")
    
    # Load and filter JSON data
    print("\n=== Loading JSON Dataset ===")
    filtered_json_data = load_and_filter_json()
    
    # Load and parse CSV data
    print("\n=== Loading CSV Dataset ===")
    parsed_data, id_groups = read_and_parse_csv()
    
    if filtered_json_data:
        print(f"\n=== JSON Summary ===")
        print(f"Filtered examples: {len(filtered_json_data)}")
        
        # Show structure of filtered data
        if filtered_json_data:
            sample = filtered_json_data[0]
            print(f"Sample keys: {list(sample.keys())}")
        
        # Save filtered JSON data
        try:
            output_path = os.path.join(output_dir, 'filtered_rag_dataset.json')
            with open(output_path, 'w') as f:
                json.dump(filtered_json_data, f, indent=2)
            print(f"✅ Saved filtered JSON data to: {output_path}")
        except Exception as e:
            print(f"❌ Error saving JSON data: {e}")
    
    if parsed_data:
        print(f"\n=== CSV Summary ===")
        print(f"Total parsed rows: {len(parsed_data)}")
        print(f"Filtered ID groups: {len(id_groups) if id_groups else 0}")
        print(f"Filtered ID groups type: {type(id_groups)}")
        
        # Show some statistics about the data
        if parsed_data:
            sample_payload = parsed_data[0]['payload']
            print(f"Sample payload type: {type(sample_payload)}")
            if isinstance(sample_payload, dict):
                print(f"Sample payload keys: {list(sample_payload.keys())}")
        
        # Filter parsed_data to keep only specific fields
        filtered_parsed_data = {}
        print(f"\n=== Filtering parsed_data ===")
        
        for item in parsed_data:
            id_val = item['id']
            payload = item['payload']
            
            # Find the corresponding pair for this ID
            if id_val in id_groups and len(id_groups[id_val]) >= 2:
                try:
                    # Extract field 1: parsed_data[id][0]['kwargs']['content'][1]['input']
                    payload1 = id_groups[id_val][0]
                    field1 = None
                    if isinstance(payload1, dict):
                        kwargs = payload1.get('kwargs', {})
                        if isinstance(kwargs, dict):
                            content = kwargs.get('content', [])
                            if isinstance(content, list) and len(content) > 1:
                                content_item = content[1]
                                if isinstance(content_item, dict) and 'input' in content_item:
                                    field1 = content_item['input']
                    
                    # Extract field 2: parsed_data[id][1]['chunk']['tools']['messages'][0]['kwargs']['content']
                    payload2 = id_groups[id_val][1]
                    field2 = None
                    if isinstance(payload2, dict):
                        chunk = payload2.get('chunk', {})
                        if isinstance(chunk, dict):
                            tools = chunk.get('tools', {})
                            if isinstance(tools, dict):
                                messages = tools.get('messages', [])
                                if isinstance(messages, list) and len(messages) > 0:
                                    message = messages[0]
                                    if isinstance(message, dict):
                                        kwargs = message.get('kwargs', {})
                                        if isinstance(kwargs, dict) and 'content' in kwargs:
                                            field2 = kwargs['content']
                    
                    # Only add if both fields were successfully extracted
                    if field1 is not None and field2 is not None:
                        filtered_parsed_data[id_val] = {
                            'input': field1,
                            'content': field2
                        }
                        print(f"✅ ID {id_val}: Both fields extracted successfully")
                    else:
                        print(f"❌ ID {id_val}: Failed to extract both fields")
                        if field1 is None:
                            print(f"   - Field 1 (input) extraction failed")
                        if field2 is None:
                            print(f"   - Field 2 (content) extraction failed")
                        
                except Exception as e:
                    print(f"❌ ID {id_val}: Error during extraction - {e}")
        
        print(f"Filtering complete. Successful extractions: {len(filtered_parsed_data)}")
        
        # Save filtered CSV data
        if filtered_parsed_data and len(filtered_parsed_data) > 0:
            try:
                output_path = os.path.join(output_dir, 'filtered_csv_data.json')
                with open(output_path, 'w') as f:
                    json.dump(filtered_parsed_data, f, indent=2)
                print(f"✅ Saved filtered CSV data to: {output_path}")
            except Exception as e:
                print(f"❌ Error saving CSV data: {e}")
        else:
            print("⚠️ No filtered CSV data to save (filtered_parsed_data is empty)")
            # Save the original parsed data as a fallback
            try:
                output_path = os.path.join(output_dir, 'original_csv_data.json')
                with open(output_path, 'w') as f:
                    json.dump(parsed_data, f, indent=2)
                print(f"✅ Saved original CSV data to: {output_path}")
            except Exception as e:
                print(f"❌ Error saving original CSV data: {e}")
    
    print(f"\n=== Combined Summary ===")
    print(f"JSON examples ready: {filtered_json_data is not None}")
    print(f"CSV data ready: {parsed_data is not None}")
    
    # Show file sizes if saved successfully
    if filtered_json_data:
        json_file_path = os.path.join(output_dir, 'filtered_rag_dataset.json')
        if os.path.exists(json_file_path):
            size = os.path.getsize(json_file_path)
            print(f"Filtered JSON file size: {size:,} bytes")
    
    if id_groups:
        csv_file_path = os.path.join(output_dir, 'filtered_csv_data.json')
        if os.path.exists(csv_file_path):
            size = os.path.getsize(csv_file_path)
            print(f"Filtered CSV file size: {size:,} bytes")
