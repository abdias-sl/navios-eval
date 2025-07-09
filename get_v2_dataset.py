#load parquet dataset from ./datasets/docVQA/0.parquet

import pandas as pd
import json
import os
from PIL import Image
import io
import numpy as np

df = pd.read_parquet("./datasets/docVQA/0.parquet", columns=['questionId', 'question', 'question_types', 'image', 'docId',
       'ucsf_document_id', 'ucsf_document_page_no', 'answers', 'data_split'])

print(df.head())
print(df.columns)
# value_counts() doesn't work on DataFrames with array/list columns
# Let's examine the data types of each column first
print("\nColumn data types:")
print(df.dtypes)

# Get basic counts of rows
print("\nTotal number of rows:", len(df))
# Get counts of each unique value in the 'question_types' column
question_types_counts = df['question_types'].explode().value_counts()
print("\nCounts of each question type:")
print(question_types_counts)
input("Press Enter to continue...")
# Get examples for each question type
print("\n=== Example rows for different question types ===")

# Filter by question types and find examples with same docId
question_types = ['layout', 'table/list', 'figure/diagram', 'Image/Photo']

selected_examples = []
saved_images = set()  # Track which images we've already saved

for q_type in question_types:
    # Filter for this question type
    filtered_df = df[df['question_types'].apply(lambda x: q_type in x)]
    
    # Get first docId that has at least 3 questions of this type
    valid_docids = filtered_df.groupby('docId').size()
    valid_docids = valid_docids[valid_docids >= 5]
    
    if len(valid_docids) > 0:
        example_docid = valid_docids.index[0]
        examples = filtered_df[filtered_df['docId'] == example_docid].head(5)
        
        print(f"\n{q_type.title()} Question Examples (DocId: {example_docid}):")
        print(examples[['question', 'answers', 'question_types', 'docId']])
        
        # Add examples to our selected list
        for _, row in examples.iterrows():
            # Convert answers to list if it's a numpy array
            answers = row['answers']
            if isinstance(answers, np.ndarray):
                answers = answers.tolist()
            elif isinstance(answers, list):
                # If it's already a list, ensure all elements are JSON serializable
                answers = [str(item) if isinstance(item, (np.integer, np.floating)) else item for item in answers]
            
            # If answers is an array, take the first element and flatten to string
            if isinstance(answers, list) and len(answers) > 0:
                first_answer = answers[0]
                # If the first element is also a list/array, flatten it
                if isinstance(first_answer, (list, np.ndarray)):
                    if isinstance(first_answer, np.ndarray):
                        first_answer = first_answer.tolist()
                    # Join all elements into a single string
                    reference_answer = " ".join(str(item) for item in first_answer)
                else:
                    reference_answer = str(first_answer)
            else:
                reference_answer = str(answers) if answers is not None else ""
            
            selected_examples.append({
                "query": row['question'],
                "reference_answer": reference_answer,
                "image_name": f"{row['docId']}.png"
            })
            
            # Save image if we haven't saved it yet
            if row['docId'] not in saved_images:
                try:
                    # Handle different image data formats
                    image_data = row['image']
                    
                    if isinstance(image_data, dict):
                        # If it's a dictionary, try to extract the image data
                        if 'bytes' in image_data:
                            img_bytes = image_data['bytes']
                        elif 'data' in image_data:
                            img_bytes = image_data['data']
                        else:
                            # Try to find any key that might contain image data
                            for key, value in image_data.items():
                                if isinstance(value, (bytes, np.ndarray)):
                                    img_bytes = value
                                    break
                            else:
                                print(f"Could not find image data in dictionary for docId {row['docId']}")
                                continue
                    elif isinstance(image_data, bytes):
                        img_bytes = image_data
                    elif isinstance(image_data, np.ndarray):
                        img_bytes = image_data.tobytes()
                    else:
                        print(f"Unexpected image data type for docId {row['docId']}: {type(image_data)}")
                        continue
                    
                    # Convert to PIL Image
                    if isinstance(img_bytes, np.ndarray):
                        img = Image.fromarray(img_bytes)
                    else:
                        img = Image.open(io.BytesIO(img_bytes))
                    
                    # Save image
                    image_path = f"./datasets/docVQA/{row['docId']}.png"
                    img.save(image_path)
                    saved_images.add(row['docId'])
                    print(f"Saved image: {image_path}")
                except Exception as e:
                    print(f"Error saving image for docId {row['docId']}: {e}")
                    print(f"Image data type: {type(row['image'])}")
                    if isinstance(row['image'], dict):
                        print(f"Image dict keys: {list(row['image'].keys())}")
    else:
        print(f"\nNo document found with 3+ {q_type} questions")

# Save the selected examples to JSON file
output_data = {
    "examples": selected_examples
}

with open("./datasets/docVQA/selected_examples.json", "w") as f:
    json.dump(output_data, f, indent=2)

print(f"\n✅ Saved {len(selected_examples)} examples to ./datasets/docVQA/selected_examples.json")
print(f"✅ Saved {len(saved_images)} unique images to ./datasets/docVQA/")
print(f"Total examples: {len(selected_examples)}")
print(f"Unique images: {len(saved_images)}")






