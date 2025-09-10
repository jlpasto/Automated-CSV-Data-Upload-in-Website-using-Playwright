import requests
import json
import os

# Define the API endpoint URL http://127.0.0.1:8000/
API_URL = "http://127.0.0.1:8000/uploadfile"  # Ensure this matches your server address and port

def test_upload_file(file_path):
    """
    Sends a file to the FastAPI endpoint for processing.
    """
    try:
        with open(file_path, "rb") as f:
            files = {'file': (os.path.basename(file_path), f, 'text/csv')}
            print(f"Attempting to upload file: {file_path}")
            response = requests.post(API_URL, files=files,timeout=60)

        # Check the response
        if response.status_code == 200:
            print("✅ Success!")
            print(json.dumps(response.json(), indent=2))
        else:
            print("❌ Failed to upload file.")
            print(f"Status Code: {response.status_code}")
            print("Response:")
            print(json.dumps(response.json(), indent=2))

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except requests.exceptions.ConnectionError as e:
        print(f"Error: Could not connect to the API server at {API_URL}. Is the server running? {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Specify the path to your CSV or Excel file
    test_csv_path = "test.csv"
    test_upload_file(test_csv_path)