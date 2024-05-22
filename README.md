
# Custom Agent

A custom websearch agent useable with Ollama, OpenAI and vLLM.

### Agent Schema:
schema/Agent Schema.png


### Prerequisites

#### Environment Setup
1. **Install Anaconda:**  
   Download Anaconda from [https://www.anaconda.com/](https://www.anaconda.com/).

2. **Create a Virtual Environment:**
   ```bash
   conda create -n agent_env python=3.10 pip
   ```
   
3. **Activate the Virtual Environment:**
   ```bash
   conda activate agent_env
   ```
#### Setup Ollama Server
1. **Download Ollama:**
   Download [https://ollama.com/download](Ollama)

2. **Download an Ollama Model:**
   ```bash
   curl http://localhost:11434/api/pull -d '{
  "name": "llama3"
}'
   ```
Ollama[https://github.com/ollama/ollama/blob/main/docs/api.md#list-local-models](API documentionation)

### Clone and Navigate to the Repository
1. **Clone the Repo:**
   ```bash
   git clone https://github.com/john-adeojo/custom_agent_tutorial.git
   ```

2. **Navigate to the Repo:**
   ```bash
   cd /path/to/your-repo/custom_agent_tutorial
   ```

3. **Install Requirements:**
   ```bash
   pip install -r requirements.txt
   ```

### Configure API Keys
1. **Open the `config.yaml`:**
   ```bash
   nano config.yaml
   ```

2. **Enter API Keys:**
   - **Serper API Key:** Get it from [https://serper.dev/](https://serper.dev/)
   - **OpenAI API Key:** Get it from [https://openai.com/](https://openai.com/)

### Run Your Query
```bash
python app.py "YOUR QUERY"
```