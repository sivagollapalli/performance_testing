from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from concurrent.futures import ThreadPoolExecutor
import json
import requests


class MyCustomToolInput(BaseModel):
    """Input schema for MyCustomTool."""
    num_requests: int = Field(..., description="No of requests that need to be sent")
    url: str = Field(..., description="HTTP API endpoint to which request has to be sent")
    method: str = Field(..., description="Type of HTTP Method to be used to send API request")

class MyCustomTool(BaseTool):
    name: str = "ParallelHTTPRequestsTool"
    description: str = (
        """
        Execute parallel HTTP requests.
        
        Args:
            num_requests (int): Number of parallel requests to send.
            url (str): The target URL for the requests.
            method (str): HTTP method (GET or POST).
        
        Returns:
            str: A summary of responses.
        """
    )
    args_schema: Type[BaseModel] = MyCustomToolInput

    def _run(self, num_requests: int, url: str, method: str) -> str:
        def send_request(index):
            """
            Helper function to send a single HTTP request.
            """
            try:
                if method.upper() == "GET":
                    response = requests.get(url)
                elif method.upper() == "POST":
                    data={
                        'post': {
                            'title': 'simple title', 
                            'description': 'simple description'
                        } 
                    }
                    response = requests.post(url, json=data)
                else:
                    return f"Request {index}: Unsupported HTTP method: {method}"
                return f"Request {index}: Status {response.status_code}, Response: {response.text}"
            except Exception as e:
                return f"Request {index}: Error: {str(e)}"

        # Run parallel requests
        with ThreadPoolExecutor(max_workers=num_requests) as executor:
            results = list(executor.map(send_request, range(1, num_requests + 1)))

        # Combine all results into a single string
        return "\n".join(results)
