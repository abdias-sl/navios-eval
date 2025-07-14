import re
import pandas as pd
import os

def parse_execution_log():
    """
    Parse execution_log.txt and extract response content from <response></response> tags
    """
    # File path
    log_file = "./execution_log.txt"
    
    # Check if file exists
    if not os.path.exists(log_file):
        print(f"❌ File not found: {log_file}")
        return
    
    print(f"📖 Reading file: {log_file}")
    
    try:
        # Read the log file
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✅ Successfully read {len(content)} characters")
        
        # Extract all response content using regex
        # Pattern to match <response>content</response>
        response_pattern = r'<response>(.*?)</response>'
        responses = re.findall(response_pattern, content, re.DOTALL)
        
        print(f"📊 Found {len(responses)} response tags")
        
        if not responses:
            print("❌ No response tags found in the file")
            return
        
        # Clean up the responses (remove extra whitespace)
        cleaned_responses = []
        for i, response in enumerate(responses, 1):
            # Remove leading/trailing whitespace and normalize
            cleaned_response = response.strip()
            cleaned_responses.append(cleaned_response)
            print(f"📝 Response {i}: {cleaned_response[:100]}..." if len(cleaned_response) > 100 else f"📝 Response {i}: {cleaned_response}")
        
        # Create DataFrame
        df = pd.DataFrame({
            'response_c37': cleaned_responses
        })
        
        # Save to CSV
        output_file = "./local_parsed_responses.csv"
        df.to_csv(output_file, index=False)
        
        print(f"\n✅ Successfully parsed {len(cleaned_responses)} responses")
        print(f"💾 Saved to: {output_file}")
        print(f"📊 DataFrame shape: {df.shape}")
        
        # Show first few rows
        print(f"\n📋 First few responses:")
        print(df.head())
        
        return df
        
    except Exception as e:
        print(f"❌ Error parsing file: {str(e)}")
        return None

def main():
    """
    Main function to run the parsing
    """
    print("=== Execution Log Parser ===")
    df = parse_execution_log()
    
    if df is not None:
        print(f"\n✅ Parsing completed successfully!")
        print(f"📊 Total responses extracted: {len(df)}")
    else:
        print(f"\n❌ Parsing failed!")

if __name__ == "__main__":
    main()
