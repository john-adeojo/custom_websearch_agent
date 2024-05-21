import requests
from bs4 import BeautifulSoup
import json
import yaml
from termcolor import colored
import os
import chardet


def load_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
        for key, value in config.items():
            os.environ[key] = value

class WebSearcher:
    """
    Input:
    Search Engine Query: The primary input to the tool is a search engine query intended for Google Search. This query is generated based on a specified plan and user query.
    Output:
    Dictionary of Website Content: The output of the tool is a dictionary where:
    The key is the URL of the website that is deemed most relevant based on the search results.
    The value is the content scraped from that website, presented as plain text.
    The source is useful for citation purposes in the final response to the user query.
    The content is used to generate a comprehensive response to the user query.
    """
    def __init__(self, model, verbose=False):
        load_config('config.yaml')
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.url = 'https://api.openai.com/v1/chat/completions'
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        self.model = model
        self.verbose = verbose

    def generate_searches(self, plan, query):
        url = "http://localhost:11434/api/generate"
        headers = {"Content-Type": "application/json"}

        payload = {
            "model": self.model,
            "prompt": f"Query: {query}\n\nPlan: {plan}",
            "format": "json",
            "system": """Return a json object that gives the input to a google search engine that could be used to find an answer to the Query based on the Plan.
            You may be given a multiple questions to answer, but you should only generate the search engine query for the single most important question according to the Plan and query. 
            The json object should have the following format:
            {
                "response": "search engine query"
            }
            """,
            "stream": False,
            "temperature": 0
        }

        try: 
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response_dict = response.json()
            response_json = json.loads(response_dict['response'])
            search_query = response_json.get('response', '')
            print(f"Search Engine Query: {search_query}")
            return search_query
        
        except Exception as e:
            print("Error in response:", response_dict)
            return "Error generating search query"
        
    def get_search_page(self, plan, query, search_results):
        url = "http://localhost:11434/api/generate"
        headers = {"Content-Type": "application/json"}

        payload = {
            "model": self.model,
            "prompt": f"Query: {query}\n\nPlan: {plan} \n\nSearch Results: {search_results}",
            "format": "json",
            "system": """Return a json object that gives the URL of the best website source to answer the Query,
            Plan and Search Results. The URL MUST be selected
            from the Search Results provided. 
            The json object should have the following format:
            {
                "response": "Best website source URL"
            }
            """,
            "stream": False,
            "temperature": 0
        }

        try: 
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response_dict = response.json()
            response_json = json.loads(response_dict['response'])
            search_query = response_json.get('response', '')
            print(f"Scraping URL: {search_query}")
            return search_query
        
        except Exception as e:
            print("Error in response:", response_dict)
            return "Error getting search page URL"
    
    def format_results(self, organic_results):

        result_strings = []
        for result in organic_results:
            title = result.get('title', 'No Title')
            link = result.get('link', '#')
            snippet = result.get('snippet', 'No snippet available.')
            result_strings.append(f"Title: {title}\nLink: {link}\nSnippet: {snippet}\n---")
        
        return '\n'.join(result_strings)
    
    def fetch_search_results(self, search_queries: str):

        search_url = "https://google.serper.dev/search"
        headers = {
            'Content-Type': 'application/json',
            'X-API-KEY': os.environ['SERPER_DEV_API_KEY']  # Ensure this environment variable is set with your API key
        }
        payload = json.dumps({"q": search_queries})
        
        # Attempt to make the HTTP POST request
        try:
            response = requests.post(search_url, headers=headers, data=payload)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4XX, 5XX)
            results = response.json()
            
            # Check if 'organic' results are in the response
            if 'organic' in results:
                return self.format_results(results['organic'])
            else:
                return "No organic results found."

        except requests.exceptions.HTTPError as http_err:
            return f"HTTP error occurred: {http_err}"
        except requests.exceptions.RequestException as req_err:
            return f"Request exception occurred: {req_err}"
        except KeyError as key_err:
            return f"Key error in handling response: {key_err}"
        
    def scrape_website_content(self, website_url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Accept-Encoding': 'gzip, deflate, br'
        }
        
        try:
            # Making a GET request to the website
            response = requests.get(website_url, headers=headers, timeout=15)
            response.raise_for_status()  # This will raise an exception for HTTP errors
            
            # Detecting encoding using chardet
            detected_encoding = chardet.detect(response.content)
            response.encoding = detected_encoding['encoding']
            
            # Parsing the page content using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text(separator='\n')
            # Cleaning up the text: removing excess whitespace
            clean_text = '\n'.join([line.strip() for line in text.splitlines() if line.strip()])

            return {"source": website_url,
                    "content": clean_text}

        except requests.exceptions.RequestException as e:
            print(f"Error retrieving content from {website_url}: {e}")
            return {website_url: f"Failed to retrieve content due to an error: {e}"}

    
    def use_tool(self, plan=None, query=None):

        search = WebSearcher(self.model)
        search_queries = search.generate_searches(plan, query)
        search_results = search.fetch_search_results(search_queries)
        best_page = search.get_search_page(search_results, plan, query)
        results_dict = search.scrape_website_content(best_page)

        if self.verbose:
            print(colored(f"SEARCH RESULTS {search_results}", 'yellow'))
            print(colored(f"BEST PAGE {best_page}", 'yellow'))
            print(colored(f"RESULTS DICT {results_dict}", 'yellow'))

        return results_dict
        

if __name__ == '__main__':

    search = WebSearcher()
    search.use_tool()
