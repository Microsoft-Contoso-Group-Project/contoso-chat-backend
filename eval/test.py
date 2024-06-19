import os
import shutil

import os
import requests
import json

def save_html_files_to_sharepoint(source_path, sharepoint_folder_url, access_token):
    try:
        # Loop through all files in the source path
        for file_name in os.listdir(source_path):
            # Check if the file has a .html extension
            if file_name.endswith(".html"):
                # Construct the full source file path
                source_file_path = os.path.join(source_path, file_name)

                # Read the HTML file content
                with open(source_file_path, 'rb') as file:
                    file_content = file.read()

                # Construct the SharePoint API endpoint URL for uploading the file
                upload_url = f"{sharepoint_folder_url}/_api/web/getfolderbyserverrelativeurl('General/Evaluations')/files/add(overwrite=true, url='{file_name}')"

                # Set the request headers
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json; odata=verbose',
                    'Accept': 'application/json; odata=verbose'
                }

                # Create the request payload
                payload = {
                    '__metadata': {
                        'type': 'SP.FileCreationInformation'
                    },
                    'overwrite': True,
                    'url': file_name,
                    'content': file_content.decode('utf-8')
                }

                # Send the POST request to upload the file to SharePoint
                response = requests.post(upload_url, headers=headers, data=json.dumps(payload))

                if response.status_code == 200:
                    print(f"HTML file uploaded successfully: {file_name}")
                else:
                    print(f"Failed to upload HTML file: {file_name}")
                    print(f"Status code: {response.status_code}")
                    print(f"Response: {response.text}")

    except FileNotFoundError:
        print(f"Source directory not found: {source_path}")
    except Exception as e:
        print(f"An error occurred while uploading the files: {str(e)}")

def save_html_files_to_local(source_path, loca_path):
    # Create the OneDrive destination directory if it doesn't exist
    os.makedirs(local_path, exist_ok=True)

    try:
        # Loop through all files in the source path
        for file_name in os.listdir(source_path):
            # Check if the file has a .html extension
            if file_name.endswith(".html"):
                # Construct the full source and destination file paths
                source_file_path = os.path.join(source_path, file_name)
                destination_file_path = os.path.join(local_path, file_name)

                # Copy the HTML file from the source path to the OneDrive path
                shutil.copy2(source_file_path, destination_file_path)
                print(f"HTML file saved successfully: {destination_file_path}")

    except FileNotFoundError:
        print(f"Source directory not found: {source_path}")
    except PermissionError:
        print(f"Permission denied while accessing the OneDrive path: {local_path}")
    except Exception as e:
        print(f"An error occurred while saving the files: {str(e)}")

source_path = '/private/var/folders/hf/3mqmr8vd3cs309p9_zg2wcsr0000gn/T/'
sharepoint_path = 'https://microsoft.sharepoint.com/:f:/r/teams/IC-ContosoHuggingFaceChatProject/Shared%20Documents/General/Evaluations?csf=1&web=1&e=5KYlsm'
local_path = f'{os.getcwd()}/contoso-chat-backend/eval/auto_eval/html_result'

#save_html_files_to_sharepoint(source_path, sharepoint_path)
save_html_files_to_local(source_path, local_path)