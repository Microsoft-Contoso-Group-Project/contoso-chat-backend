import json

# Path to the .ipynb file
notebook_path = 'path_to_your_notebook.ipynb'
'''
# Read the notebook
with open(notebook_path, 'r') as file:
    notebook = json.load(file)

# Navigate through the notebook to the cell with the output you want
# This example assumes you want the output of the first cell that contains code
for cell in notebook['cells']:
    if cell['cell_type'] == 'code':
        # Check if the cell has outputs
        if 'outputs' in cell:
            outputs = cell['outputs']
            # Assume we want the first output object
            if outputs:
                output_data = outputs[0]
                if 'text' in output_data:
                    print(output_data['text'])
                elif 'data' in output_data and 'text/plain' in output_data['data']:
                    print(output_data['data']['text/plain'])
        break

'''


import os
dir_path = "/Users/yonghuizhu/.promptflow/.runs"
"/2024_06_11_000810chat_base_run"

files = [  ]
for file in os.listdir(dir_path):
    if file.startswith
    files.append(file)