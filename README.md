
# Custom Agent

A custom websearch agent useable with Ollama, SearXNG, and vLLM.

### Agent schema:
![Agent Schema](schema/Agent%20Schema.png)


### Prerequisites

#### Environment setup
1. **Install Anaconda:**  
   Download and install [https://www.anaconda.com/](Anaconda).

2. **Create and activate your virtual environment:**
   ```bash
   conda create -n agent_env python pip
   conda activate agent_env
   ```

#### Clone the repository and install the requirements
   ```bash
   git clone https://github.com/manjaroblack/custom_websearch_agent.git
   cd custom_websearch_agent
   pip install -r requirements.txt
   ```

#### Setup Ollama Server
1. **Download and install Ollama:**
   [https://ollama.com/download](Ollama)

2. **Create a custom Model:**
   ```bash
   ollama create llama3_agentic -f ./MODELFILE
   ```

#### Setup and configure a SearXNG server
1. **Setup a SearXNG Server:**
   Repo: [https://github.com/searxng/searxng](SearXNG)

2. **Configure SearXNG**
   Copy the files in the SearXNG folder to your settings location
      1. /etc/searxng
      2. /usr/local/searxng

### Run your query
```bash
python agent.py run
```
Then enter your query.
