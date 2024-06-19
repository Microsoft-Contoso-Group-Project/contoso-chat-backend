import pandas as pd
import os

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