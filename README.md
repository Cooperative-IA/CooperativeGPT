Certainly! Here's the organized README in Markdown format:

# MELTING POT INSTALLATIONS

## Prerequisites

Before you start with the Melting Pot installations, please ensure you have the required tools and environments set up.

### 1. **Install Bazel:**

Bazel is a tool that automates software builds and tests.

```bash
sudo apt install apt-transport-https curl gnupg -y
curl -fsSL https://bazel.build/bazel-release.pub.gpg | gpg --dearmor > bazel-archive-keyring.gpg
sudo mv bazel-archive-keyring.gpg /usr/share/keyrings
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/bazel-archive-keyring.gpg] https://storage.googleapis.com/bazel-apt stable jdk1.8" | sudo tee /etc/apt/sources.list.d/bazel.list
sudo apt update && sudo apt install bazel
sudo apt update && sudo apt full-upgrade
sudo apt install bazel-1.0.0
```

> **Note:** If the above steps do not work, use `sudo apt install bazel`. If required, install Python (step 2) first.

### 2. **Install Python 3.10+**

As of 21/09/2023, everything is working on Python 3.10.

```bash
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.10
```

### 3. **Set Up a Virtual Environment with Python 3.10**

```bash
sudo apt install python3.10 python3.10-dev python3.10-venv
python3.10 -m venv "nombre_del_ambiente"
source "nombre"/bin/activate    # Activate the created 3.10 environment
```

### 4. **Navigate to the Repository Folder and Install Dependencies**

```bash
pip install --editable .[dev]
```

### 5. **Test the Installation**

```bash
pytest --pyargs meltingpot
```

---

# COOPERATIVE AI SETUP

Follow the steps below to set up the Cooperative AI environment:

### 1. **Clone the Repository**

Clone the Cooperative AI repository.

```bash
git clone https://github.com/Cooperative-IA/CooperativeGPT/
```

### 2. **Configure the .ENV File**

Create and configure your own `.ENV` file to store API keys and local paths. This includes configuring the melting pot source.

### 3. **Install the Required Dependencies**

```bash
pip install openai scikit-image chromadb tiktoken AzureOpenAI
sudo apt-get install python3-tk
```

If you are getting following error while trying to run chromadb example code using my python3.10.8 venv3.10:
File "~/venv3.10/lib/python3.10/site-packages/chromadb/__init__.py", line 36, in <module> raise RuntimeError( RuntimeError: Your system has an unsupported version of sqlite3. Chroma requires sqlite3 >= 3.35.0.

Execute following steps to resolve this error:

Inside my python3.10.8's virtual environment i.e. venv3.10, installed pysqlite3-binary using command: pip install pysqlite3-binary
Added these 3 lines in **venv3.10/lib/python3.10/site-packages/chromadb/__init__.py** at the beginning:

```python
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
```


### 4. **Run the Application**

Test the setup by running the main script:

```bash
python main.py
```

### 5. Running Simulations

To run the simulation, use the following command:

```bash
python main.py [--substrate SUBSTRATE] [--scenario SCENARIO] [--players PLAYER1 PLAYER2 ...] [--record RECORD]
```

#### Arguments

- `--substrate`: Specifies the name of the game to run. The name must match a folder in `game_environment/substrates/python`. Default is `commons_harvest_language`.
- `--scenario`: Specifies the name of the scenario to run. This must be one of the predefined scenarios for the chosen game. Default is `commons_harvest__open_0`.
- `--players`: Specifies a list of player names to run the game with. Provide each player name as a separate argument. Default is `Juan`, `Laura`, `Pedro`.
- `--record`: Specifies whether to record the game. Acceptable values are `True` or `False`. Default is `True`.

#### Examples

Run the simulation with specific values:

```bash
python main.py --substrate "your_game_name" --scenario "your_scenario_name" --players Player1 Player2 Player3 --record True
```

Run the simulation with default values for substrate, scenario, and record, but specify player names:

```bash
python main.py --players Alice Bob Charlie
```

Run the simulation with all default values:

```bash
python main.py
```




