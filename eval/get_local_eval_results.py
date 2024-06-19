import os
import json
import pandas as pd
from datetime import datetime
class MetricsLoader:
    def __init__(self, base_directory):
        self.base_directory = base_directory
        self.all_metrics = {}

    def load_metrics_from_runs(self):
        # Access the directory containing all runs
        full_path = os.path.join(self.base_directory, '.promptflow', '.runs')
        
        # List all subdirectories that end with "chat_eval_run"
        for entry in os.listdir(full_path):
            if entry.endswith("chat_eval_run") and os.path.isdir(os.path.join(full_path, entry)):
                # Construct the path to the metrics.json file
                metrics_path = os.path.join(full_path, entry, 'metrics.json')
                print(entry)
                
                if os.path.isfile(metrics_path):
                    # Load the metrics.json file
                    with open(metrics_path, 'r') as file:
                        metrics_data = json.load(file)
                        self.all_metrics[entry] = metrics_data

    def create_metrics_table(self, config_list):
        def _add_to_row(configs, metrics):
            data_row = {
                'Model': configs["model_name"],
                'Max tokens': max_tokens_look_up[configs["model_name"]],  # Placeholder for Max tokens
                'Top_p': configs["top_p"],
                'Embedding': configs['embedding'],  # Placeholder for Temperature
                'Template': 'original',  # Placeholder for template
                'Coherence': metrics.get('gpt_coherence', ''),
                'Coherence_pass_rate': metrics.get('gpt_coherence_pass_rate(%)', ''),
                'Groundedness': metrics.get('gpt_groundedness', ''),
                'Groundedness_pass_rate': metrics.get('gpt_groundedness_pass_rate(%)', ''),
                'Fluency': metrics.get('gpt_fluency', ''),
                'Fluency_pass_rate': metrics.get('gpt_fluency_pass_rate(%)', ''),
                'Relevance': metrics.get('gpt_relevance', ''),
                'Relevance_pass_rate': metrics.get('gpt_relevance_pass_rate(%)', ''),
                'Notebook_path': os.path.join(os.getcwd(), "contoso-chat-backend", "eval", "auto_eval", 
                        f"{configs['model_name']}_top{configs['top_p']}_emb{configs['embedding']}_{configs['template']}template.ipynb"),
                'Run_id': run_id
            }
            return data_row

        def _save_metrics_to_runs(all_metrics):
            # Access the directory containing all runs
            full_path = os.path.join(self.base_directory, '.promptflow', '.runs')
            
            # Iterate over all entries in self.all_metrics
            for entry, metrics_data in self.all_metrics.items():
            
                # Construct the path to the metrics.json file
                metrics_path = os.path.join(full_path, entry, 'metrics.json')
                    
                # Ensure the directory exists
                if os.path.isdir(os.path.join(full_path, entry)):
                    # Save the metrics_data back to the metrics.json file
                    with open(metrics_path, 'w') as file:
                        json.dump(metrics_data, file, indent=4)
                    print(f"Metrics saved for {entry}")

        # Define the DataFrame columns
        columns = [
            'Model', 'Max tokens', 'Top_p', 'Embedding', 'Template',
            'Coherence', 'Coherence_pass_rate', 
            'Groundedness', 'Groundedness_pass_rate', 
            'Fluency', 'Fluency_pass_rate', 
            'Relevance', 'Relevance_pass_rate', 'Notebook_path', 'Run_id'
        ]

        max_tokens_look_up = {
            'meta_llama3_instruct_8B': 8000, 'meta_llama3_instruct_70B': 8000,
            'meta_llama3_8B': 8000, 'meta_llama3_70B': 8000, 
            'Phi_3_mini_4k_instruct': 4000, 'Phi_3_mini_128k_instruct': 128000, 
            'google_gemma': 8000, 'Mixtral': 32000
        }

        # Prepare list to store all the data rows
        data_rows = []
        
        # Temporary dictionary to hold filtered metrics
        filtered_metrics = {}
        outstanding_metrics = {}
        
        for run_id, metrics in self.all_metrics.items():
            if 'config' in metrics.keys():
                filtered_metrics[run_id] = metrics
                print(f"Existing metrics is {run_id}") 
            else:
                outstanding_metrics[run_id] = metrics
                print(f"New metrics is {run_id} as it lacks 'config' in metrics")

        existing_config = {}
        outstanding_config = []
        existing_config_keys = [(metrics['config']['model_name'], metrics['config']['top_p'], metrics['config']['embedding'], metrics['config']['template']) for metrics in filtered_metrics.values()]
        
        for run_id, metrics in filtered_metrics.items():  # Load existing run with same configuration
            configs = metrics['config']
            data_row = _add_to_row(configs, metrics)
            data_rows.append(data_row)
            existing_config[run_id] = configs

        for config in config_list:
            # Create a tuple of keys from config that uniquely identifies it
            config_keys = (config['model_name'], config['top_p'], config['embedding'], config['template'])  # Adjust keys as per your actual structure
            
            if config_keys not in existing_config_keys:
                outstanding_config.append(config)

        # Remove runs from outstanding_metrics that have a date before the specified date
        date = datetime.now().strftime("%Y-%m-%d")
        
        outstanding_metrics = {run_id: metrics for run_id, metrics in outstanding_metrics.items() if run_id[:10] >= date}

        print("outstanding_config", outstanding_config)
        print("outstanding metric", outstanding_metrics.keys())

        for idx, (run_id, metrics) in enumerate(outstanding_metrics.items()):  # Add current run 
            data_row = _add_to_row(outstanding_config[idx], metrics)
            data_rows.append(data_row)
            self.all_metrics[run_id]['config'] = outstanding_config[idx]

        _save_metrics_to_runs(all_metrics=self.all_metrics)

        # Creating DataFrame
        return pd.DataFrame(data_rows, columns=columns)

if __name__ == '__main__':
    config_list = [
        {"model_name": 'Phi_3_mini_4k_instruct', "top_p": 0.1, "embedding": "text-embedding-ada-002", 'template': 'original'},
        {"model_name": 'Phi_3_mini_4k_instruct', "top_p": 0.1, "embedding": "text-embedding-ada-002", 'template': 'original'},
        {"model_name": 'Phi_3_mini_4k_instruct', "top_p": 0.1, "embedding": "text-embedding-ada-002", 'template': 'original'},
        {"model_name": 'Phi_3_mini_4k_instruct', "top_p": 0.1, "embedding": "text-embedding-ada-002", 'template': 'original'}
    ]

    base_directory = '/Users/yonghuizhu'
    loader = MetricsLoader(base_directory)
    loader.load_metrics_from_runs()
    metrics_table = loader.create_metrics_table(config_list)

    # Save the DataFrame to Excel
    file_name = 'metrics_data.xlsx'
    metrics_table.to_excel(file_name, index=False)
    print(metrics_table)
