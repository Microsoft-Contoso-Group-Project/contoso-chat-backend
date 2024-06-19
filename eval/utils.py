import pandas as pd
import yaml
import os
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import subprocess
import json
import re
import shutil

def get_pf_connection_list():
    try:
        # Run the command and capture the output
        result = subprocess.run(['pf', 'connection', 'list'], capture_output=True, text=True)
        
        # Check for errors
        if result.returncode != 0:
            print("Error running command:", result.stderr)
            return None
        
        # Parse the JSON output
        connections = json.loads(result.stdout)
        return connections
    except Exception as e:
        print("An error occurred:", str(e))
        return None

def update_vector_search_dimensions(notebook_path, new_dimension_value):
    # Load the notebook
    with open(notebook_path) as f:
        nb = nbformat.read(f, as_version=4)
    
    # Iterate over all cells to find the one that defines `vector_search_dimensions`
    for cell in nb.cells:
        if cell.cell_type == 'code':
            # Check for the specific line of code that needs to be updated
            if 'vector_search_dimensions=' in cell.source:
                # Replace the existing dimension value with the new one
                cell.source = re.sub(
                    r"(vector_search_dimensions=)(\d+)",
                    r"\g<1>{}".format(new_dimension_value),
                    cell.source
                )

    # Save the modified notebook back to the same file
    with open(notebook_path, 'w') as f:
        nbformat.write(nb, f)
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

# Custom loader and dumper to maintain order
class OrderedLoader(yaml.SafeLoader):
    pass

class OrderedDumper(yaml.SafeDumper):
    pass

def load_yaml(file_path):
    with open(file_path, 'r') as file:
        data = yaml.load(file, Loader=OrderedLoader)
    return data

def save_yaml(data, file_path):
    with open(file_path, 'w') as file:
        yaml.dump(data, file, Dumper=OrderedDumper, default_flow_style=False)

def modify_yaml(data, llm_connection, embedding,llm_top_p):
    for node in data.get('nodes', []):
        if node['name'] == 'llm_response':
            if 'connection' in node:
                node['connection'] = llm_connection
            if 'inputs' in node:
                node['inputs']['top_p'] = llm_top_p
        elif node['name'] == "custom_question_embedding":
            if 'inputs' in node:
                node['inputs']['connection'] = embedding[0]
                node['inputs']['deployment_name']=embedding[1]
    return data

def run_notebook(notebook_path, output_path):
    print(output_path)
    print("output_path_for_ipynb_exist:",os.path.exists(output_path))
    with open(notebook_path) as f:
        nb = nbformat.read(f, as_version=4)
    ep = ExecutePreprocessor(timeout=500, kernel_name='python3')
    try:
        ep.preprocess(nb, {'metadata': {'path': os.path.dirname(notebook_path)}})
        with open(output_path, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)
        print(f"Notebook executed and saved as {output_path}.")
    except Exception as e:
        print(f"Error occurred: {e}")

def run_eval_script_ipynb(eval_script_path, config):
    output_dir = os.path.join(os.path.dirname(eval_script_path),"auto_eval")
    os.makedirs(output_dir, exist_ok=True)
    # Building the path
    output_path = os.path.join(os.getcwd(), "contoso-chat-backend", "eval", "auto_eval", 
                           f"{config['model_name']}_top{config['top_p']}_emb{config['embedding']}_{config['template']}template.ipynb")
    run_notebook(eval_script_path, output_path)


    
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

def get_top_k_configurations(file_path, k, weights, output_file):
    # Load the Excel file into a DataFrame
    df = pd.read_excel(file_path)
    
    # Calculate the weighted score for each configuration
    df['weighted_score'] = (
        weights['coherence'] * df['Coherence'] +
        weights['coherence_pass_rate'] * df['Coherence_pass_rate'] +
        weights['groundedness'] * df['Groundedness'] +
        weights['groundedness_pass_rate'] * df['Groundedness_pass_rate'] +
        weights['fluency'] * df['Fluency'] +
        weights['fluency_pass_rate'] * df['Fluency_pass_rate'] +
        weights['relevance'] * df['Relevance'] +
        weights['relevance_pass_rate'] * df['Relevance_pass_rate']
    )
    
    # Sort the DataFrame by the weighted score in descending order
    df_sorted = df.sort_values(by='weighted_score', ascending=False)
    
    # Select the top-k configurations
    top_k_configurations = df_sorted.head(k)
    
    # Save the top-k configurations to a new Excel file
    top_k_configurations.to_excel(output_file, index=False)
    
    # Return the top-k configurations
    return top_k_configurations[['Model', 'Max tokens', 'Top_p', 'Embedding', 'Template']]
def save_html_files_to_local(source_path, local_path):
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


if __name__ == '__main__':
    print(os.getcwd())
    file_path = f'{os.getcwd()}/metrics_data.xlsx'
    top_k = 3
    weights = {
        'coherence': 0.2,
        'coherence_pass_rate': 0.1,
        'groundedness': 0.2,
        'groundedness_pass_rate': 0.1,
        'fluency': 0.2,
        'fluency_pass_rate': 0.1,
        'relevance': 0.2,
        'relevance_pass_rate': 0.1
    }
    output_file = f'{os.getcwd()}/contoso-chat-backend/eval/auto_eval/top_{top_k}_configurations.xlsx'

    top_configurations = get_top_k_configurations(file_path, top_k, weights, output_file)
    print(top_configurations)