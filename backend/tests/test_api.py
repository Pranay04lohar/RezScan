import requests
import os
import json
import time
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from fpdf import FPDF  # We'll use FPDF to create test PDF files

# Disable SSL warnings for testing
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def wait_for_server(max_retries=5, delay=2):
    """Wait for the server to be ready"""
    for i in range(max_retries):
        try:
            response = requests.get('http://127.0.0.1:5000/api/health', verify=False)
            if response.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            if i < max_retries - 1:
                print(f"Waiting for server to start... (attempt {i+1}/{max_retries})")
                time.sleep(delay)
            continue
    return False

def test_health_endpoint():
    """Test the health check endpoint"""
    print("\nTesting Health Check Endpoint...")
    try:
        response = requests.get('http://127.0.0.1:5000/api/health', verify=False)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure the Flask application is running.")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_root_endpoint():
    """Test the root endpoint"""
    print("\nTesting Root Endpoint...")
    try:
        response = requests.get('http://127.0.0.1:5000/', verify=False)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure the Flask application is running.")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def create_test_pdf(content, output_path):
    """Create a test PDF file with the given content"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Split content into lines and add to PDF
    for line in content.split('\n'):
        pdf.cell(200, 10, txt=line, ln=True)
    
    pdf.output(output_path)

def test_match_endpoint():
    """Test the resume matching endpoint"""
    print("\nTesting Resume Matching Endpoint...")
    
    # Check if test files exist
    test_files_dir = os.path.join(os.path.dirname(__file__), 'test_files')
    if not os.path.exists(test_files_dir):
        print(f"Creating test files directory: {test_files_dir}")
        os.makedirs(test_files_dir)
    
    # Create sample test files
    jd_path = os.path.join(test_files_dir, 'test_jd.pdf')
    resume_path = os.path.join(test_files_dir, 'test_resume.pdf')
    
    # Create sample content
    jd_content = """Python Developer
Required Skills: Python, Flask, SQL
Experience: 3+ years"""
    
    resume_content = """Experienced Python Developer
Skills: Python, Flask, SQL, Django
Experience: 5 years"""
    
    # Create PDF files
    create_test_pdf(jd_content, jd_path)
    create_test_pdf(resume_content, resume_path)
    
    try:
        # Prepare files for upload
        with open(jd_path, 'rb') as jd_file, open(resume_path, 'rb') as resume_file:
            # Create multipart form data
            files = {
                'job_description': ('test_jd.pdf', jd_file, 'application/pdf'),
                'resumes': ('test_resume.pdf', resume_file, 'application/pdf')
            }
            
            # Prepare parameters
            data = {
                'technique': 'tfidf',
                'similarity_metric': 'cosine',
                'top_k': 5,
                'similarity_threshold': 0.3
            }
            
            # Make the request
            response = requests.post('http://127.0.0.1:5000/api/match', 
                                   files=files, 
                                   data=data,
                                   verify=False)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("\nMatching Results:")
                print(json.dumps(result, indent=2))
                return True
            else:
                print(f"Error Response: {response.json()}")
                return False
                
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure the Flask application is running.")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
    finally:
        # Clean up test files
        try:
            for file_path in [jd_path, resume_path]:
                if os.path.exists(file_path):
                    os.remove(file_path)
        except Exception as e:
            print(f"Warning: Could not remove test file {file_path}: {str(e)}")

def main():
    """Run all tests"""
    print("Starting API Tests...")
    print("Make sure the Flask application is running on http://127.0.0.1:5000")
    
    # Wait for server to be ready
    if not wait_for_server():
        print("Error: Could not connect to the server. Please make sure the Flask application is running.")
        return
    
    # Test health endpoint
    health_ok = test_health_endpoint()
    print(f"Health Check {'PASSED' if health_ok else 'FAILED'}")
    
    # Test root endpoint
    root_ok = test_root_endpoint()
    print(f"Root Endpoint {'PASSED' if root_ok else 'FAILED'}")
    
    # Test match endpoint
    match_ok = test_match_endpoint()
    print(f"Match Endpoint {'PASSED' if match_ok else 'FAILED'}")
    
    # Print summary
    print("\nTest Summary:")
    print(f"Health Check: {'✓' if health_ok else '✗'}")
    print(f"Root Endpoint: {'✓' if root_ok else '✗'}")
    print(f"Match Endpoint: {'✓' if match_ok else '✗'}")
    
    if all([health_ok, root_ok, match_ok]):
        print("\nAll tests PASSED! The API is working properly.")
    else:
        print("\nSome tests FAILED. Please check the errors above.")

if __name__ == '__main__':
    main() 