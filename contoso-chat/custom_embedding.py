import requests
from typing import List
from promptflow.core import tool
from promptflow.connections import ServerlessConnection

@tool
def custom_question_embedding(question: str, connection: ServerlessConnection, deployment_name: str) -> List[float]:
    API_URL = connection.configs["api_base"]
    headers = {"Authorization": f"Bearer {connection.secrets['api_key']}"}
    
    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    
    output = query({"inputs": question})

    
    return output