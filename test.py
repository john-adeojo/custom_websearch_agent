import requests
import json

def run_planning_agent(self, query, plan=None, outputs=None, feedback=None):
    url = self.url
    headers = self.headers

    system_prompt = self.planning_agent_prompt.format(
            outputs=outputs,
            plan=plan,
            feedback=feedback,
            tool_specs=self.tool_specs
        )

    payload = {
        "model": self.model,
        "prompt": query,
        "format": "json",
        "system": system_prompt,
        "stream": False,
        "temperature": 0.5
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    response_dict = response.json()

    if 'response' in response_dict:
        normal_response = response_dict['response']
        print(f"Generated Response: {normal_response}")
        return normal_response
    else:
        print("Error in response:", response_dict)
        return None

# Example usage
query = "How can I plan my weekend trip?"
system_prompt = "Provide detailed suggestions for planning a weekend trip."
result = run_planning_agent(query, system_prompt)
print(result)
