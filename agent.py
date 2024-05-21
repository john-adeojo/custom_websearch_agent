import os 
import yaml
import json
import requests
from datetime import datetime, timezone
from termcolor import colored
from prompts import planning_agent_prompt, integration_agent_prompt, check_response_prompt
from search import WebSearcher


def load_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
        for key, value in config.items():
            os.environ[key] = value

def get_current_utc_datetime():
    now_utc = datetime.now(timezone.utc)
    current_time_utc = now_utc.strftime("%Y-%m-%d %H:%M:%S %Z")
    return current_time_utc

class Agent:
    def __init__(self, model, model_tool, model_qa, tool, temperature=0, max_tokens=1000, planning_agent_prompt=None, integration_agent_prompt=None, check_response_prompt=None, verbose=False, iterations=5, model_endpoint=None, server=None):
        self.server = server
        self.model_endpoint = model_endpoint
        self.headers = {"Content-Type": "application/json"}
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.tool_specs = tool.__doc__
        self.planning_agent_prompt = planning_agent_prompt
        self.integration_agent_prompt = integration_agent_prompt
        self.model = model
        self.tool = tool(model=model_tool, verbose=verbose, model_endpoint=model_endpoint, server=server)
        self.iterations = iterations
        self.model_qa = model_qa

    def run_planning_agent(self, query, plan=None, outputs=None, feedback=None):

        system_prompt = self.planning_agent_prompt.format(
                outputs=outputs,
                plan=plan,
                feedback=feedback,
                tool_specs=self.tool_specs,
                datetime=get_current_utc_datetime()
            )
        
        if self.server == 'ollama':
            payload = {
                "model": self.model,
                "prompt": query,
                "system": system_prompt,
                "stream": False,
                "temperature": 0,
            }

        if self.server == 'runpod':
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "stream": False,
                "temperature": 0,
                "stop": "<|eot_id|>"
            }

        try:
            response = requests.post(self.model_endpoint, headers=self.headers, data=json.dumps(payload))
            response_dict = response.json()

            if self.server == 'ollama':
                response = response_dict['response']
            
            if self.server == 'runpod':
                response = response_dict['choices'][0]['message']['content']

            print(colored(f"Planning Agent: {response}", 'blue'))
            return response
        
        except Exception as e:
            print("Error in response:", response_dict)
            return "Error generating plan {e}"
        
    def run_integration_agent(self, query, plan=None, outputs=None, reason=None, previous_response=None):

        system_prompt = self.integration_agent_prompt.format(
                outputs=outputs,
                plan=plan,
                reason=reason,
                sources=outputs.get('sources', ''),
                previous_response=previous_response
            )
        
        if self.server == 'ollama':
            payload = {
                "model": self.model,
                "prompt": query,
                "system": system_prompt,
                "stream": False,
                "temperature": 0,
            }

        if self.server == 'runpod':
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "stream": False,
                "temperature": 0,
                "stop": "<|eot_id|>"
            }

        try:
            response = requests.post(self.model_endpoint, headers=self.headers, data=json.dumps(payload))
            response_dict = response.json()

            if self.server == 'ollama':
                response = response_dict['response']
            
            if self.server == 'runpod':
                response = response_dict['choices'][0]['message']['content']

            print(colored(f"Integration Agent: {response}", 'green'))

            return response
        
        except Exception as e:
            print("Error in response:", response_dict)
            return "Error generating plan {e}"
    
    def check_response(self, response, query):

        if self.server == 'ollama':
            payload = {
                "model": self.model_qa,
                "prompt": f"query: {query}\n\nresponse: {response}",
                "format": "json",
                "system": check_response_prompt,
                "stream": False,
                "temperature": 0,
                "stop": "<|eot_id|>"
            }

        if self.server == 'runpod':
            payload = {
                "model": self.model,
                "response_format": {"type": "json_object"},
                "messages": [
                    {
                        "role": "system",
                        "content": check_response_prompt
                    },
                    {
                        "role": "user",
                        "content": f"query: {query}\n\nresponse: {response}"
                    }
                ],
                "temperature": 0,
                "stop": "<|eot_id|>"
            }

        try: 
            response = requests.post(self.model_endpoint, headers=self.headers, data=json.dumps(payload))
            response_dict = response.json()

            if self.server == 'ollama':
                decision_dict = json.loads(response_dict['response'])

            if self.server == 'runpod':
                response_content = response_dict['choices'][0]['message']['content']
                decision_dict = json.loads(response_content)
            
            return decision_dict
        
        except Exception as e:
            print("Error in assessing response quality:", response_dict)
            return "Error in assessing response quality"
         
    def execute(self):
        query = input("Enter your query: ")
        meets_requirements = False
        plan = None
        outputs = None
        response = None
        reason = None
        previous_response = None
        iterations = 0
    
        while not meets_requirements and iterations < self.iterations:
            iterations += 1  
            plan = self.run_planning_agent(query, plan=plan, outputs=outputs, feedback=response)
            outputs = self.tool.use_tool(plan=plan, query=query)
            integration_agent_response = self.run_integration_agent(query, plan, outputs, reason=reason, previous_response=previous_response)
            previous_response = integration_agent_response
            response_dict = self.check_response(integration_agent_response, query)
            meets_requirements = response_dict.get('pass', '')
            print(f"Response meets requirements: {meets_requirements}")
            if meets_requirements == 'True':
                meets_requirements = True
            else: 
                meets_requirements = False
                reason = response_dict.get('reason', '')
            # citations = response_dict.get('citations', '')

            # if citations == 'No citations':
            #     integration_agent_response = self.run_integration_agent(query, plan=plan, outputs=outputs, reason=reason, previous_response=previous_response)
            #     previous_response = integration_agent_response
            #     response_dict = self.check_response(integration_agent_response, query)
            #     meets_requirements = response_dict.get('pass', '')
            #     if meets_requirements == 'True':
            #         meets_requirements = True
            #     else: 
            #         meets_requirements = False
            #     reason = response_dict.get('reason', '')

        print(colored(f"Final Response: {integration_agent_response}", 'cyan'))

        
if __name__ == '__main__':

    # Params for Ollama
    # model = "llama3:instruct"
    # model_tool = "llama3:instruct"
    # model_qa = "llama3:instruct"
    # model_endpoint = 'http://localhost:11434/api/generate'
    # server = 'ollama'

    # Params for RunPod
    model = "meta-llama/Meta-Llama-3-70B-Instruct"
    model_tool = "meta-llama/Meta-Llama-3-70B-Instruct"
    model_qa = "meta-llama/Meta-Llama-3-70B-Instruct"
    runpod_endpoint = 'https://2pglgilg5fgfa9-8000.proxy.runpod.net/'
    completions_endpoint = 'v1/chat/completions'
    model_endpoint = runpod_endpoint + completions_endpoint
    server = 'runpod'

    agent = Agent(model=model,
                  model_tool=model_tool,
                  model_qa=model_qa,
                  tool=WebSearcher, 
                  planning_agent_prompt=planning_agent_prompt, 
                  integration_agent_prompt=integration_agent_prompt,
                  verbose=True,
                  iterations=2,
                  model_endpoint=model_endpoint,
                  server=server
                  )
    agent.execute()


    

