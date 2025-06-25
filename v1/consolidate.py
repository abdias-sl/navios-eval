import json
import os
from typing import List, Dict, Any

def consolidate_datasets():
    """
    Consolidate filtered_csv_data.json and filtered_rag_dataset.json
    """
    try:
        # Load the filtered CSV data
        csv_file_path = './datasets/out/filtered_csv_data.json'
        with open(csv_file_path, 'r') as f:
            csv_data = json.load(f)
        
        print(f"✅ Loaded CSV data: {len(csv_data)} entries")
        print(f"CSV data type: {type(csv_data)}")
        
        # Load the filtered RAG dataset
        rag_file_path = './datasets/out/filtered_rag_dataset.json'
        with open(rag_file_path, 'r') as f:
            rag_data = json.load(f)
        
        print(f"✅ Loaded RAG data: {len(rag_data)} entries")
        print(f"RAG data type: {type(rag_data)}")
        
        # Take only the first 10 entries from RAG dataset
        rag_data_trimmed = rag_data[:10]
        print(f"📏 Trimmed RAG data to first 10 entries")
        
        # Get CSV data as a list (assuming it's a dict with IDs as keys)
        csv_entries = list(csv_data.values())
        print(f"📋 CSV entries as list: {len(csv_entries)} items")
        
        # Verify we have matching counts
        if len(csv_entries) != len(rag_data_trimmed):
            print(f"⚠️ Warning: Mismatch in entry counts")
            print(f"   CSV entries: {len(csv_entries)}")
            print(f"   RAG entries: {len(rag_data_trimmed)}")
            print(f"   Using minimum count: {min(len(csv_entries), len(rag_data_trimmed))}")
        
        # Consolidate the data
        consolidated_data = []
        min_count = min(len(csv_entries), len(rag_data_trimmed))
        
        for i in range(min_count):
            csv_entry = csv_entries[i]
            rag_entry = rag_data_trimmed[i]
            
            # Parse the nested JSON string in CSV input
            processed_csv_entry = csv_entry.copy()
            if 'input' in processed_csv_entry:
                try:
                    # Parse the JSON string to extract the actual input text
                    input_json = json.loads(processed_csv_entry['input'])
                    if isinstance(input_json, dict) and 'input' in input_json:
                        processed_csv_entry['input'] = input_json['input']
                        print(f"✅ Entry {i+1}: Parsed nested JSON input")
                    else:
                        print(f"⚠️ Entry {i+1}: Unexpected JSON structure in input")
                except json.JSONDecodeError as e:
                    print(f"❌ Entry {i+1}: Failed to parse JSON input - {e}")
                except Exception as e:
                    print(f"❌ Entry {i+1}: Error processing input - {e}")
            
            # Parse the content array string in CSV data
            if 'content' in processed_csv_entry:
                try:
                    # Parse the array string to extract pageContent values
                    content_array = json.loads(processed_csv_entry['content'])
                    if isinstance(content_array, list):
                        page_contents = []
                        for item in content_array:
                            if isinstance(item, dict) and 'type' in item and 'text' in item:
                                # Handle new format: {'type': 'text', 'text': '{"pageContent":"some text"}'}
                                try:
                                    text_json = json.loads(item['text'])
                                    if isinstance(text_json, dict) and 'pageContent' in text_json:
                                        page_contents.append(text_json['pageContent'])
                                    else:
                                        print(f"⚠️ Entry {i+1}: Text JSON missing pageContent key")
                                except json.JSONDecodeError:
                                    print(f"⚠️ Entry {i+1}: Failed to parse text JSON")
                            elif isinstance(item, dict) and 'pageContent' in item:
                                # Handle old format: {'pageContent': 'some text'}
                                page_contents.append(item['pageContent'])
                            else:
                                print(f"⚠️ Entry {i+1}: Item missing expected structure")
                        
                        processed_csv_entry['content'] = page_contents
                        print(f"✅ Entry {i+1}: Extracted {len(page_contents)} pageContent values from CSV")
                    else:
                        print(f"⚠️ Entry {i+1}: CSV content is not an array")
                except json.JSONDecodeError as e:
                    print(f"❌ Entry {i+1}: Failed to parse CSV content array - {e}")
                except Exception as e:
                    print(f"❌ Entry {i+1}: Error processing CSV content - {e}")
            
            # Create consolidated entry
            consolidated_entry = {
                'csv_data': processed_csv_entry,
                'rag_data': rag_entry
            }
            
            consolidated_data.append(consolidated_entry)
            
            # Show sample of first entry
            if i == 0:
                print(f"\n=== Sample Consolidated Entry {i+1} ===")
                print(f"CSV data keys: {list(processed_csv_entry.keys())}")
                print(f"RAG data keys: {list(rag_entry.keys())}")
                if 'input' in processed_csv_entry:
                    print(f"CSV input: {processed_csv_entry['input'][:100]}..." if len(processed_csv_entry['input']) > 100 else f"CSV input: {processed_csv_entry['input']}")
                if 'content' in processed_csv_entry:
                    content_count = len(processed_csv_entry['content'])
                    print(f"CSV content: {content_count} pageContent items")
                    if content_count > 0:
                        first_content = processed_csv_entry['content'][0]
                        print(f"  First content: {first_content[:100]}..." if len(first_content) > 100 else f"  First content: {first_content}")
                if 'query' in rag_entry:
                    print(f"RAG query: {rag_entry['query'][:100]}..." if len(rag_entry['query']) > 100 else f"RAG query: {rag_entry['query']}")
        
        print(f"\n✅ Consolidated {len(consolidated_data)} entries")
        
        # Save consolidated data
        output_path = './datasets/out/consolidated_dataset.json'
        with open(output_path, 'w') as f:
            json.dump(consolidated_data, f, indent=2)
        
        print(f"💾 Saved consolidated dataset to: {output_path}")
        
        # Show file size
        if os.path.exists(output_path):
            size = os.path.getsize(output_path)
            print(f"📊 File size: {size:,} bytes")
        
        # Show summary statistics
        print(f"\n=== Summary ===")
        print(f"Original CSV entries: {len(csv_data)}")
        print(f"Original RAG entries: {len(rag_data)}")
        print(f"Trimmed RAG entries: {len(rag_data_trimmed)}")
        print(f"Consolidated entries: {len(consolidated_data)}")
        
        return consolidated_data
        
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error consolidating datasets: {e}")
        return None

if __name__ == "__main__":
    print("=== Dataset Consolidation ===")
    consolidated_data = consolidate_datasets()
    
    if consolidated_data:
        print(f"\n✅ Consolidation successful!")
        print(f"Final dataset has {len(consolidated_data)} entries")
    else:
        print(f"\n❌ Consolidation failed!")
