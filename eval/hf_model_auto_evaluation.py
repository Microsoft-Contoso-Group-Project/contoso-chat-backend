import os
from get_local_eval_results import MetricsLoader
from utils import *

def auto_evaluate_model(yaml_path, models, top_ps, embeddings, templates, HF_endpoints, eval_script_path, runs_config_log_path, use_exist):
    cur_vector_dimension = 0
    config_list = []

    synch_runs_and_eval_log()

    # Load existing configurations from the log file if it exists
    if os.path.exists(runs_config_log_path) and os.path.getsize(runs_config_log_path) != 0:
        with open(runs_config_log_path, 'r') as file:
            existing_configs = json.load(file)
    else:
        existing_configs = []

    # Iterate over all combinations of models, top_p values, embeddings, and templates
    print("existing",existing_configs)
    for embedding in embeddings:
        for top_p in top_ps:
            for model_name in models:
                for template in templates:
                    config = {"model_name": model_name, "top_p": top_p, "embedding": embedding, "template": template}
                    config_list.append(config)
                    print("---" * 30)
                    print(f"Current Model: {model_name}, top_p: {top_p}, embedding: {embedding}")
                    print("+++" * 30)

                    # Check if the current configuration already exists and skip if specified
                    if config in existing_configs and use_exist:
                        print(f"\033[93mSkipping existing configuration: {config}\033[0m")
                        continue

                    if model_name in HF_endpoints.keys():
                        new_yaml_path = yaml_path.replace("flow_b.dag.yaml", "flow.dag.yaml")
                        print(f"embedding:{embedding}, tuple: {isinstance(embedding, tuple)}")

                        if isinstance(embedding, tuple):
                            yaml_path = yaml_path.replace("flow_b.dag.yaml", "flow_custom_b.dag.yaml")
                            data = load_yaml(yaml_path)
                            modified_data = modify_yaml(data, model_name, embedding, top_p)

                            # Update the vector search dimensions if necessary
                            if cur_vector_dimension != embedding[2]:
                                notebook_path = "contoso-chat-backend/data/product_info/create-azure-search_custom_embedding.ipynb"
                                update_vector_search_dimensions(notebook_path, new_dimension_value=embedding[2])
                                run_notebook(notebook_path, output_path=notebook_path)
                                cur_vector_dimension = embedding[2]
                                print("embedding index update completed")
                        else:
                            # Update the vector search dimensions if necessary
                            if cur_vector_dimension != 1536:
                                notebook_path = "contoso-chat-backend/data/product_info/create-azure-search.ipynb"
                                update_vector_search_dimensions(notebook_path, new_dimension_value=1536)
                                run_notebook(notebook_path, output_path=notebook_path)
                                cur_vector_dimension = 1536
                                print("embedding index update completed")

                            data = load_yaml(yaml_path)
                            modified_data = modify_yaml(data, model_name, embedding, top_p)

                        save_yaml(modified_data, new_yaml_path)

                        try:
                            run_eval_script_ipynb(eval_script_path, config)
                        except Exception as e:
                            print(f"Error occurred: {e}")
                            config_list.pop()
                    else:
                        print("\033[91mError, model not found in established connections. Try adding it in .../connections/create-connections.ipynb\033[0m")

    return config_list

if __name__ == '__main__':
    '''
    Make sure your terminal is run one level above contoso-chat-backend due to relative paths
    '''
    connections = get_pf_connection_list()
    if connections is not None:
        api_base_mapping = {conn['name']: conn['api_base'] for conn in connections if 'api_base' in conn}
        print("pf_connection:", api_base_mapping.keys())
    else:
        print("Failed to retrieve connections.")

    models = ["Phi_3_mini_4k_instruct", 'meta_llama3_instruct_70B']
    top_ps = [0.1, 0.5, 0.9]
    embeddings = ["text-embedding-ada-002",["bge-large","bge-large-en-v1.5",1024]]
    templates = ['original']
    yaml_path = 'contoso-chat-backend/contoso-chat_hf/flow_b.dag.yaml'
    eval_script_path = 'contoso-chat-backend/eval/evaluate-chat-prompt-flow_local.ipynb'
    runs_config_log_path = os.getcwd() + '/contoso-chat-backend/eval/auto_eval/runs_config_log.json'

    # Evaluate the models with the specified configurations
    config_list = auto_evaluate_model(yaml_path, models, top_ps, embeddings, 
                                      templates, api_base_mapping, 
                                      eval_script_path, runs_config_log_path, use_exist=True)

    # Update the configuration log file with the new configurations
    if os.path.getsize(runs_config_log_path) != 0:
        with open(runs_config_log_path, 'r') as file:
            old_config_list = json.load(file)
        for runs in config_list:
            if runs in old_config_list:
                continue
            old_config_list.append(runs)
        new_config_list = old_config_list
    else:
        new_config_list = config_list

    with open(runs_config_log_path, 'w') as file:
        json.dump(new_config_list, file, indent=4)
    

    base_directory = '/Users/yonghuizhu'
    loader = MetricsLoader(base_directory)
    loader.load_metrics_from_runs()
    metrics_table = loader.create_metrics_table(config_list=config_list)

    # Save the metrics table to an Excel file
    file_name = 'metrics_data.xlsx'
    metrics_table.to_excel(file_name, index=False)
    print("full_metric_table", metrics_table)

    file_path = f'{os.getcwd()}/metrics_data.xlsx'
    top_k = 5
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

    # Get the top k configurations based on the specified weights
    top_configurations = get_top_k_configurations(file_path, top_k, weights, output_file)
    print("top_K_table", top_configurations)

    source_path = '/private/var/folders/hf/3mqmr8vd3cs309p9_zg2wcsr0000gn/T/'
    local_path = f'{os.getcwd()}/contoso-chat-backend/eval/auto_eval/html_result'
    save_html_files_to_local(source_path, local_path)



