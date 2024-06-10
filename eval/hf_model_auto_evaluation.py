import yaml
import os
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

import subprocess
import json
import re

from get_local_eval_results import MetricsLoader

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
    with open(notebook_path) as f:
        nb = nbformat.read(f, as_version=4)
    ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
    try:
        ep.preprocess(nb, {'metadata': {'path': os.path.dirname(notebook_path)}})
        with open(output_path, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)
        print(f"Notebook executed and saved as {output_path}.")
    except Exception as e:
        print(f"Error occurred: {e}")

def run_eval_script_ipynb(eval_script_path, model_name, top_p):
    output_dir = os.path.join(os.path.dirname(eval_script_path),"auto_eval")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{model_name}_top{top_p}.ipynb")
    run_notebook(eval_script_path, output_path)

def auto_evaluate_model(yaml_path, models, top_ps, embeddings, HF_endpoints, eval_script_path):
    for model_name in models:
        for top_p in top_ps:
            for embedding in embeddings:
                
                print(f"Current Model: {model_name}, top_p: {top_p}")
                if model_name in HF_endpoints.keys():
                    new_yaml_path = yaml_path.replace("flow_b.dag.yaml","flow.dag.yaml")
                    if isinstance(embedding,tuple) or embedding != "text-embedding-ada-002":
                        yaml_path = yaml_path.replace("flow_b.dag.yaml","flow_custom_b.dag.yaml")
                        data = load_yaml(yaml_path)
                        modified_data = modify_yaml(data, model_name, embedding, top_p)
                        notebook_path = "contoso-chat-backend/data/product_info/create-azure-search_custom_embedding.ipynb"
                        update_vector_search_dimensions(notebook_path, new_dimension_value=embedding[2])
                        run_notebook(notebook_path,output_path=notebook_path)
                    else:
                        data = load_yaml(yaml_path)
                        modified_data = modify_yaml(data, model_name, embedding,top_p)
                    save_yaml(modified_data, new_yaml_path)
                    run_eval_script_ipynb(eval_script_path, model_name, top_p)
                else:
                    print("Error, model not found in established connection try adding it in .../connections/create-connections.ipynb")
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
    
if __name__ == '__main__':
    '''
    '''
    connections = get_pf_connection_list()
    if connections is not None:
        api_base_mapping = {conn['name']: conn['api_base'] for conn in connections if 'api_base' in conn}
        print(api_base_mapping.keys())
    else:
        print("Failed to retrieve connections.")

    models = ["meta_llama3_instruct_70B"]
    top_ps = [0.1]
    embeddings=[("bge-large","bge-large-en-v1.5",1024)] #"text-embedding-ada-002"
    
    yaml_path = 'contoso-chat-backend/contoso-chat_hf/flow_b.dag.yaml' #evaluate-chat-prompt-flow_local will run the flow.dag.yaml, and flow_b.dag.yaml is used as a template'
    eval_script_path = 'contoso-chat-backend/eval/evaluate-chat-prompt-flow_local.ipynb'
    auto_evaluate_model(yaml_path, models, top_ps, embeddings, api_base_mapping, eval_script_path)

    base_directory = '/Users/yonghuizhu'
    loader = MetricsLoader(base_directory)
    loader.load_metrics_from_runs(date='2024_06_09')
    metrics_table = loader.create_metrics_table()

    # Save the DataFrame to Excel
    file_name = 'metrics_data.xlsx'
    metrics_table.to_excel(file_name, index=False)
    print(metrics_table)
    
    



