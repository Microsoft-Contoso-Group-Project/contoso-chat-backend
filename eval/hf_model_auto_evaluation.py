import yaml
import os
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

import subprocess
import json

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

def modify_yaml(data, llm_connection, llm_top_p):
    for node in data.get('nodes', []):
        if node['name'] == 'llm_response':
            if 'connection' in node:
                node['connection'] = llm_connection
            if 'inputs' in node:
                node['inputs']['top_p'] = llm_top_p
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

def auto_evaluate_model(yaml_path, models, top_ps, HF_endpoints, eval_script_path):
    for model_name in models:
        for top_p in top_ps:
            print(f"Current Model: {model_name}, top_p: {top_p}")
            if model_name in HF_endpoints.keys():
                data = load_yaml(yaml_path)
                modified_data = modify_yaml(data, model_name, top_p)
                new_yaml_path = yaml_path.replace("flow_b.dag.yaml","flow.dag.yaml")
                save_yaml(modified_data, new_yaml_path)
                run_eval_script_ipynb(eval_script_path, model_name, top_p)
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
    
if __name__ == '__main__':
    connections = get_pf_connection_list()
    if connections is not None:
        api_base_mapping = {conn['name']: conn['api_base'] for conn in connections if 'api_base' in conn}
        print(api_base_mapping.keys())
    else:
        print("Failed to retrieve connections.")

    models = ["meta_llama3_instruct_70B"]
    top_ps = [0.1]
    yaml_path = 'contoso-chat-backend/contoso-chat_hf/flow_b.dag.yaml'
    eval_script_path = 'contoso-chat-backend/eval/evaluate-chat-prompt-flow_local.ipynb'
    auto_evaluate_model(yaml_path, models, top_ps, api_base_mapping, eval_script_path)
