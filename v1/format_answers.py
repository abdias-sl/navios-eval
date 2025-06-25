import pandas as pd
import json
import os
from typing import List, Dict, Any

def format_answers_csv():
    """
    Read answers.csv file, format to JSON, and handle duplicate thread_ids
    """
    try:
        # Read the CSV file
        csv_file_path = './datasets/answers.csv'
        df = pd.read_csv(csv_file_path)
        
        print(f"✅ Loaded answers CSV. Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print(f"\nFirst few rows:")
        print(df.head())
        
        # Check for duplicate thread_ids
        duplicate_counts = df['thread_id'].value_counts()
        duplicates = duplicate_counts[duplicate_counts > 1]
        
        if len(duplicates) > 0:
            print(f"\n⚠️ Found {len(duplicates)} thread_ids with duplicates:")
            for thread_id, count in duplicates.items():
                print(f"  thread_id: {thread_id} - {count} occurrences")
        else:
            print(f"\n✅ No duplicate thread_ids found")
        
        # Remove duplicates by keeping first occurrence of each thread_id
        df_deduplicated = df.drop_duplicates(subset=['thread_id'], keep='first')
        
        print(f"\n📊 After deduplication:")
        print(f"  Original rows: {len(df)}")
        print(f"  After deduplication: {len(df_deduplicated)}")
        print(f"  Removed {len(df) - len(df_deduplicated)} duplicate rows")
        
        # Convert to JSON format with thread_id as key and content as value
        json_data = {}
        for index, row in df_deduplicated.iterrows():
            # Get the thread_id as key
            thread_id = row['thread_id']
            
            # Get the content/answer as value
            content = row['content'] if not pd.isna(row['content']) else None
            
            # Extract text after </ToolCall> if it exists
            if content and isinstance(content, str):
                toolcall_index = content.find('</ToolCall>')
                if toolcall_index != -1:
                    # Get text after </ToolCall>
                    content = content[toolcall_index + len('</ToolCall>'):].strip()
                    print(f"✅ Entry {index + 1}: Extracted text after </ToolCall>")
                else:
                    print(f"⚠️ Entry {index + 1}: No </ToolCall> tag found, keeping original content")
            
            # Use thread_id as key and content as value
            json_data[thread_id] = content
        
        print(f"\n✅ Converted to JSON format: {len(json_data)} records")
        
        # Show sample of converted data
        if json_data:
            print(f"\n=== Sample JSON Record ===")
            first_thread_id = list(json_data.keys())[0]
            sample_content = json_data[first_thread_id]
            print(f"Key (thread_id): {first_thread_id}")
            if isinstance(sample_content, str) and len(sample_content) > 100:
                print(f"Value (content): {sample_content[:100]}...")
            else:
                print(f"Value (content): {sample_content}")
        
        # Create output directory if it doesn't exist
        output_dir = './datasets/out'
        os.makedirs(output_dir, exist_ok=True)
        
        # Save to JSON file
        output_path = os.path.join(output_dir, 'formatted_answers.json')
        with open(output_path, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        print(f"\n💾 Saved formatted answers to: {output_path}")
        
        # Show file size
        if os.path.exists(output_path):
            size = os.path.getsize(output_path)
            print(f"📊 File size: {size:,} bytes")
        
        # Show summary statistics
        print(f"\n=== Summary ===")
        print(f"Original CSV rows: {len(df)}")
        print(f"Unique thread_ids: {len(df_deduplicated)}")
        print(f"Duplicate rows removed: {len(df) - len(df_deduplicated)}")
        print(f"Final JSON records: {len(json_data)}")
        
        return json_data
        
    except FileNotFoundError:
        print(f"❌ File not found: {csv_file_path}")
        return None
    except Exception as e:
        print(f"❌ Error processing answers CSV: {e}")
        return None

if __name__ == "__main__":
    print("=== Answers CSV Formatting ===")
    formatted_data = format_answers_csv()
    
    if formatted_data:
        print(f"\n✅ Formatting successful!")
        print(f"Final dataset has {len(formatted_data)} records")
    else:
        print(f"\n❌ Formatting failed!")
