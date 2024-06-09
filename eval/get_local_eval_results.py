import os
import json
import pandas as pd

class MetricsLoader:
    def __init__(self, base_directory):
        self.base_directory = base_directory
        self.all_metrics = {}

    def load_metrics_from_runs(self, date='2024_06_09'):
        # Access the directory containing all runs
        full_path = os.path.join(self.base_directory, '.promptflow', '.runs')

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
                        self.all_metrics[entry] = metrics_data

    def create_metrics_table(self):
        # Define the DataFrame columns
        columns = [
            'Model', 'Max tokens', 'Temperature', 'Template',
            'Coherence', 'Coherence_pass_rate', 
            'Groundedness', 'Groundedness_pass_rate', 
            'Fluency', 'Fluency_pass_rate', 
            'Relevance', 'Relevance_pass_rate', 'Run_id'
        ]

        # Prepare list to store all the data rows
        data_rows = []
        
        # Process each metrics data in all_metrics
        for run_id, metrics in self.all_metrics.items():
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
        return pd.DataFrame(data_rows, columns=columns)

if __name__ == '__main__':
    base_directory = '/Users/yonghuizhu'
    loader = MetricsLoader(base_directory)
    loader.load_metrics_from_runs()
    metrics_table = loader.create_metrics_table()

    # Save the DataFrame to Excel
    file_name = 'metrics_data.xlsx'
    metrics_table.to_excel(file_name, index=False)
    print(metrics_table)
