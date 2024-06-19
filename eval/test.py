import os
import json
import shutil
# Function to count folders in a directory
def count_folders(directory):
    if os.path.exists(directory):
        return sum(os.path.isdir(os.path.join(directory, item)) for item in os.listdir(directory))
    else:
        return 0

# Function to count elements in the JSON file
def count_json_elements(json_file):
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            data = json.load(f)
            return len(data)
    else:
        return 0

# Function to delete the two latest folders in a directory
def delete_latest_folders(directory, num_folders_to_delete):
    if os.path.exists(directory):
        folders = [os.path.join(directory, item) for item in os.listdir(directory) if os.path.isdir(os.path.join(directory, item))]
        folders.sort(key=os.path.getmtime, reverse=True)
        
        for i in range(min(num_folders_to_delete, len(folders))):
            folder_to_delete = folders[i]
            print(f"Deleting folder: {folder_to_delete}")
            shutil.rmtree(folder_to_delete)
    else:
        print(f"Directory {directory} does not exist.")

def synch_runs_and_eval_log(json_file_path = 'contoso-chat-backend/eval/auto_eval/runs_config_log.json'
                            ,runs_directory = '.promptflow/.runs'):
    
    root = os.getcwd()

    # Remove the last component
    path_components = root.split(os.sep)
    root_without_last = os.sep.join(path_components[:-1])

    full_runs_directory = os.path.join(root_without_last,runs_directory)
    full_json_file_path = os.path.join(root,json_file_path)
    # Count folders in .promptflow/.runs
    num_folders = count_folders(full_runs_directory)

    # Count elements in runs_config_log.json
    num_json_elements = count_json_elements(full_json_file_path)
    
    
    print(f"Number of runs in log:{num_json_elements}, Number of runs in promptflow:{num_folders}")
    

    # Check the condition
    if num_folders == 2 * num_json_elements:
        print(f"\033[93mThe number of folders in {runs_directory} is exactly twice the number of elements in {json_file_path}.\033[0m")
    else:
        print(f"The condition is not met: The number of folders in {runs_directory} is not twice the number of elements in {json_file_path}.")
        
        # Delete the two latest folders if the condition is not met
        num_folders_to_delete = 2
        delete_latest_folders(full_runs_directory, num_folders_to_delete)
    

synch_runs_and_eval_log()