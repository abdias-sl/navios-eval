import os
from dotenv import load_dotenv
import requests
import json

def upload_to_knowledge_base():
    """
    Upload all files from ./datasets/final-dataset to the knowledge base
    """
    # Load environment variables
    load_dotenv()

    # Get credentials from environment variables
    email = os.getenv('email')
    password = os.getenv('password')
    
    # Prepare login request
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }

    login_data = {
        "email": email,
        "password": password,
        "new_session": False
    }
    
    # Make login request
    print("🔐 Authenticating...")
    response = requests.post(
        "https://auth.shyftos.shyftops.io/rbac/auth/login",
        headers=headers,
        json=login_data,
    )

    if response.status_code == 200 or response.status_code == 201:
        access_token = response.json().get("access_token")
        print("✅ Authentication successful")
    else:
        raise Exception(f"Login failed with status code: {response.status_code}")

    # Source directory
    source_dir = "./datasets/final-dataset/"
    
    # Check if source directory exists
    if not os.path.exists(source_dir):
        print(f"❌ Source directory not found: {source_dir}")
        return
    
    # Get all files in the directory
    files_to_upload = []
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            file_path = os.path.join(root, file)
            files_to_upload.append(file_path)
    
    print(f"📁 Found {len(files_to_upload)} files to upload")
    
    if not files_to_upload:
        print("❌ No files found in the source directory")
        return
    
    # Project ID and endpoint
    project_id = "46ec05bd-a783-47ad-a9aa-ebcdfb768e63"
    upload_url = f"http://localhost:8000/api/projects/{project_id}/knowledge-bases/upload"
    
    # Set up headers with authentication
    headers = {
        'Authorization': f'Bearer {access_token}',
        'accept': '*/*'
    }
    
    # Upload each file
    successful_uploads = 0
    failed_uploads = 0
    upload_results = []
    
    for i, file_path in enumerate(files_to_upload, 1):
        filename = os.path.basename(file_path)
        print(f"\n🔄 Uploading file {i}/{len(files_to_upload)}: {filename}")
        
        try:
            # Determine MIME type based on file extension
            file_extension = os.path.splitext(file_path)[1].lower()
            mime_type = 'text/plain'  # default
            
            if file_extension in ['.jpg', '.jpeg']:
                mime_type = 'image/jpeg'
            elif file_extension == '.png':
                mime_type = 'image/png'
            elif file_extension == '.gif':
                mime_type = 'image/gif'
            elif file_extension == '.pdf':
                mime_type = 'application/pdf'
            elif file_extension == '.json':
                mime_type = 'application/json'
            elif file_extension in ['.csv', '.xlsx', '.xls']:
                mime_type = 'text/csv' if file_extension == '.csv' else 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            elif file_extension in ['.txt', '.md']:
                mime_type = 'text/plain'
            
            # Prepare the multipart form data
            with open(file_path, 'rb') as file:
                files = {
                    'file': (filename, file, mime_type),
                    'title': (None, filename)
                }
                
                # Make the POST request
                response = requests.post(
                    upload_url,
                    headers=headers,
                    files=files
                )
            
            # Check if request was successful
            if response.status_code == 200 or response.status_code == 201:
                print(f"✅ Successfully uploaded: {filename}")
                successful_uploads += 1
                
                # Store upload result
                upload_results.append({
                    'filename': filename,
                    'status': 'success',
                    'response': response.json() if response.content else None
                })
            else:
                print(f"❌ Failed to upload {filename}: Status {response.status_code}")
                print(f"Response: {response.text}")
                failed_uploads += 1
                
                upload_results.append({
                    'filename': filename,
                    'status': 'failed',
                    'status_code': response.status_code,
                    'error': response.text
                })
                
        except Exception as e:
            print(f"❌ Error uploading {filename}: {str(e)}")
            failed_uploads += 1
            
            upload_results.append({
                'filename': filename,
                'status': 'error',
                'error': str(e)
            })
    
    # Print summary
    print(f"\n📊 Upload Summary:")
    print(f"✅ Successful uploads: {successful_uploads}")
    print(f"❌ Failed uploads: {failed_uploads}")
    print(f"📁 Total files processed: {len(files_to_upload)}")
    
    # Save upload results to JSON file
    upload_summary = {
        'project_id': project_id,
        'upload_url': upload_url,
        'source_directory': source_dir,
        'total_files': len(files_to_upload),
        'successful_uploads': successful_uploads,
        'failed_uploads': failed_uploads,
        'upload_results': upload_results
    }
    
    with open("knowledge_base_upload_results.json", "w") as f:
        json.dump(upload_summary, f, indent=2)
    
    print(f"💾 Upload results saved to knowledge_base_upload_results.json")
    
    return upload_summary

if __name__ == "__main__":
    print("=== Knowledge Base Upload ===")
    results = upload_to_knowledge_base()
    
    if results:
        print(f"\n✅ Upload process completed!")
        print(f"📊 Final results: {results['successful_uploads']} successful, {results['failed_uploads']} failed")
    else:
        print(f"\n❌ Upload process failed!")
