import anthropic
import os
import base64
from PIL import Image
import io
import json
from dotenv import load_dotenv
import base64
import httpx

def encode_image_to_base64(image_path):
    """
    Encode an image to base64 format
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        tuple: (base64_data, media_type)
    """
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
    
    # Determine media type based on file extension
    if image_path.endswith('.png'):
        media_type = "image/png"
    elif image_path.endswith('.jpg') or image_path.endswith('.jpeg'):
        media_type = "image/jpeg"
    else:
        media_type = "image/png"  # default
    
    # Encode to base64
    base64_data = base64.b64encode(image_data).decode('utf-8')
    
    return base64_data, media_type

def load_examples_data():
    """
    Load the selected examples from JSON file
    
    Returns:
        dict: Dictionary mapping image names to their data
    """
    json_path = "./datasets/docVQA/bigger-subset/selected_examples.json"
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # Create a mapping from image_name to example data
        examples_map = {}
        for example in data['examples']:
            image_name = example['image_name']
            examples_map[image_name] = {
                'query': example['query'],
                'reference_answer': example['reference_answer']
            }
        
        print(f"📄 Loaded {len(examples_map)} examples from {json_path}")
        return examples_map
        
    except FileNotFoundError:
        print(f"❌ JSON file not found: {json_path}")
        return {}
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON format in {json_path}")
        return {}

def create_contextual_prompt(image_name, query, reference_answer):
    """
    Create a contextual prompt based on the image and example data
    
    Args:
        image_name (str): Name of the image file
        query (str): Original query
        reference_answer (str): Reference answer
        
    Returns:
        str: Formatted prompt
    """
    prompt = f"""You are looking at an image file named "{image_name}". 

Based on what you can see in this image, I want you to:

1. **Rephrase the original question** to be more verbose and contextual, incorporating details about what you observe in the image. The original question was: "{query}"

2. **Provide a more detailed answer** that expands on the reference answer while being faithful to the information visible in the image. The reference answer was: "{reference_answer}"

Please structure your response as follows:

**Rephrased Question:**
[Your verbose, contextual version of the question]

**Detailed Answer:**
[Your expanded answer based on the image content]

Make sure your rephrased question and detailed answer are grounded in what you can actually see in the image, and provide additional context about the document type, layout, or content that would help someone understand the broader context."""
    
    return prompt

def process_images_in_directory():
    """
    Process all images in the docVQA/bigger-subset directory
    """
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment variables")
        print("Please set your Anthropic API key in the .env file or environment")
        return
    
    # Initialize Anthropic client
    try:
        client = anthropic.Anthropic(api_key=api_key)
        print("✅ Anthropic client initialized successfully")
    except TypeError as e:
        if "proxies" in str(e):
            # Try alternative initialization for older versions
            try:
                client = anthropic.Anthropic()
                print("✅ Anthropic client initialized successfully (using default config)")
            except Exception as e2:
                print(f"❌ Error with alternative initialization: {str(e2)}")
                return
        else:
            print(f"❌ Error initializing Anthropic client: {str(e)}")
            return
    except Exception as e:
        print(f"❌ Error initializing Anthropic client: {str(e)}")
        print("This might be due to a version compatibility issue.")
        print("Try updating the anthropic package: pip install --upgrade anthropic")
        return
    
    # Load examples data
    examples_map = load_examples_data()
    
    if not examples_map:
        print("❌ No examples data loaded. Exiting.")
        return
    
    # Directory containing images
    image_directory = "./datasets/docVQA/bigger-subset/"
    
    # Check if directory exists
    if not os.path.exists(image_directory):
        print(f"❌ Directory not found: {image_directory}")
        return
    
    # Get all image files
    image_extensions = ['.png', '.jpg', '.jpeg']
    image_files = []
    
    for filename in os.listdir(image_directory):
        if any(filename.lower().endswith(ext) for ext in image_extensions):
            image_files.append(os.path.join(image_directory, filename))
    
    print(f"📁 Found {len(image_files)} images in {image_directory}")
    
    if not image_files:
        print("❌ No image files found in the directory")
        return
    
    # Store all results
    enhanced_examples = []
    
    # Process each image
    for i, image_path in enumerate(image_files, 1):
        image_filename = os.path.basename(image_path)
        print(f"\n🔄 Processing image {i}/{len(image_files)}: {image_filename}")
        
        # Check if we have example data for this image
        if image_filename not in examples_map:
            print(f"⚠️  No example data found for {image_filename}, skipping...")
            continue
        
        try:
            # Get example data for this image
            example_data = examples_map[image_filename]
            query = example_data['query']
            reference_answer = example_data['reference_answer']
            
            # Create contextual prompt
            prompt = create_contextual_prompt(image_filename, query, reference_answer)
            
            # Encode image to base64
            image_data, media_type = encode_image_to_base64(image_path)
            
            # Create message for Claude API
            message = client.messages.create(
                model="claude-3-7-sonnet-20250219",  # Updated to current model
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    }
                ],
            )
            
            # Get the model's response
            model_response = message.content[0].text
            
            # Parse the response to extract rephrased question and detailed answer
            rephrased_question = ""
            detailed_answer = ""
            
            # Try to extract the structured response
            if "**Rephrased Question:**" in model_response and "**Detailed Answer:**" in model_response:
                parts = model_response.split("**Rephrased Question:**")
                if len(parts) > 1:
                    question_part = parts[1].split("**Detailed Answer:**")
                    if len(question_part) > 1:
                        rephrased_question = question_part[0].strip()
                        detailed_answer = question_part[1].strip()
                    else:
                        rephrased_question = question_part[0].strip()
            else:
                # If structured format not found, use the whole response
                rephrased_question = model_response
                detailed_answer = model_response
            
            # Create enhanced example
            enhanced_example = {
                "query": query,  # Original query
                "reference_answer": reference_answer,  # Original reference answer
                "image_name": image_filename,
                "rephrased_question": rephrased_question,
                "detailed_answer": detailed_answer,
                "full_model_response": model_response
            }
            
            enhanced_examples.append(enhanced_example)
            
            # Print the response
            print(f"✅ Successfully processed {image_filename}")
            print(f"📝 Rephrased Question: {rephrased_question[:150]}...")
            print(f"📝 Detailed Answer: {detailed_answer[:150]}...")
                    
        except Exception as e:
            print(f"❌ Error processing {image_filename}: {str(e)}")
            continue
    # Save results to new JSON file
    output_data = {
        "examples": enhanced_examples
    }
    
    output_filename = "./datasets/docVQA/bigger-subset/enhanced_examples.json"
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n✅ Completed processing {len(image_files)} images")
    print(f"💾 Saved {len(enhanced_examples)} enhanced examples to {output_filename}")
    print(f"📊 Summary: {len(enhanced_examples)} examples processed successfully")

if __name__ == "__main__":
    print("=== Image Processing with Claude API ===")
    process_images_in_directory()
