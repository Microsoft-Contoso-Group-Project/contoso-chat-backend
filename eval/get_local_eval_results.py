import os
import json
import pandas as pd

def load_metrics_from_runs(base_directory, date='2024_06_09'):
    # This dictionary will hold all the metrics loaded, keyed by the directory name
    all_metrics = {}
    
    # Access the directory containing all runs
    full_path = os.path.join(base_directory, '.promptflow', '.runs')
    
    # List all subdirectories that start with the specified date
    for entry in os.listdir(full_path):
        if entry.startswith(date) and os.path.isdir(os.path.join(full_path, entry)):
            # Construct the path to the metrics.json file
            metrics_path = os.path.join(full_path, entry, 'metrics.json')
            
            # Check if the metrics.json file exists
            if os.path.isfile(metrics_path):
                # Load the metrics.json file
                with open(metrics_path, 'r') as file:
                    metrics_data = json.load(file)
                    all_metrics[entry] = metrics_data
    
    return all_metrics

def create_metrics_table(all_metrics):
    # Define the DataFrame columns
    columns = [
        'Model', 'Max tokens', 'Temperature', 'Template',
        'Coherence', 'Coherence_pass_rate', 
        'Groundedness', 'Groundedness_pass_rate', 
        'Fluency', 'Fluency_pass_rate', 
        'Relevance', 'Relevance_pass_rate','Run_id'
    ]
    
    # Prepare list to store all the data rows
    data_rows = []
    
    # Process each metrics data in all_metrics
    print(all_metrics)
    for run_id, metrics in all_metrics.items():
        print(run_id)
        data_row = {
            'Model': '',  # Placeholder for Model
            'Max tokens': '',  # Placeholder for Max tokens
            'Temperature': '',  # Placeholder for Temperature
            'Template': '',  # Placeholder for template
            'Coherence': metrics.get('gpt_coherence', ''),
            'Coherence_pass_rate': metrics.get('gpt_coherence_pass_rate(%)', ''),
            'Groundedness': metrics.get('gpt_groundedness', ''),
            'Groundedness_pass_rate': metrics.get('gpt_groundedness_pass_rate(%)', ''),
            'Fluency': metrics.get('gpt_fluency', ''),
            'Fluency_pass_rate': metrics.get('gpt_fluency_pass_rate(%)', ''),
            'Relevance': metrics.get('gpt_relevance', ''),
            'Relevance_pass_rate': metrics.get('gpt_relevance_pass_rate(%)', ''),
            'Run_id': run_id
        }
        data_rows.append(data_row)
    
    # Creating DataFrame
    df = pd.DataFrame(data_rows, columns=columns)
    
    return df

if __name__ == '__main__':
    '''
    replace the base directory to the directory that the output files is saved to when running evaluate-chat-flow_local,ipynb
    '''
    base_directory = '/Users/yonghuizhu'
    all_metrics = load_metrics_from_runs(base_directory)
    
    # Create and print the DataFrame
    metrics_table = create_metrics_table(all_metrics)
    file_name= 'metrics_data.xlsx'
    print(metrics_table.keys())
    metrics_table.to_excel(file_name, index=False)

    
    
