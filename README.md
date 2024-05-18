# Chatbot with Session Memory and Vectorstore Retrieval

This project is a chatbot application with a Python backend and a React frontend. The chatbot leverages session memory and a vectorstore to retrieve information. The frontend is a custom and simple interface using React, and the connection between the backend and frontend is established using WebSockets.

## Features

- **Session Memory**: Maintains conversation context across multiple interactions.
- **Vectorstore Retrieval**: Retrieves relevant information from a vectorstore to answer queries.
- **WebSocket Communication**: Real-time communication between the frontend and backend.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Installation

### Backend

1. **Clone the repository**:
    ```bash
    git clone https://github.com/nydasco/rag_based_chatbot.git
    cd rag_based_chatbot
    ```

2. **Set up folders and LLM**:
    ```bash
    mkdir processed
    mkdir to_process
    mkdir backend/llm
    ```
    Download `Meta-Llama-3-8B-Instruct-Q8_0.gguf` from HuggingFace into the `backend/llm` folder.

3. **Set up a virtual environment**:
    ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate
    ```

4. **Install the required dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

5. **Upload some data**:
    Place pdf files to process into the `/to_process` folder.
    ```bash
    python process_files.py
    ```

6. **Run the backend server**:
    ```bash
    python backend.py
    ```

### Frontend

1. **Navigate to the frontend directory**:
    ```bash
    cd nydasbot
    ```

2. **Install the required dependencies**:
    ```bash
    npm install
    ```

3. **Start the frontend development server**:
    ```bash
    npm start
    ```

## Usage

Once both the backend and frontend servers are running, open your web browser and navigate to `http://localhost:3000`. You should see the chatbot interface.

- Type your message in the input field and press `Enter` or click the "Send" button.
- The chatbot will process your message and respond based on the session context and retrieved information from the vectorstore.

## Configuration

The backend configuration is managed through a `parameters.toml` file. This has been configured to work, however you may want to change some of the setting to better suit your environment.