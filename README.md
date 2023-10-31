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
pip install openai scikit-image chromadb tiktoken
sudo apt-get install python3-tk
```

### 4. **Run the Application**

Test the setup by running the main script:

```bash
python main.py
```



