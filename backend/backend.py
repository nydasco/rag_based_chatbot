import asyncio
import json
import websockets
import logging
import tomli
from warnings import simplefilter
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings

simplefilter(action="ignore", category=FutureWarning)

class ConfigLoader:
    def __init__(self, filepath):
        self.config = self.load_config(filepath)
    
    def load_config(self, filepath):
        """
        Loads the configuration from the given file.

        Args:
            filepath (str): The path to the TOML file.

        Returns:
            dict: The loaded configuration.

        """
        with open(filepath, "rb") as params:
            return tomli.load(params)

class RAGModel:
    def __init__(self, config):
        self.config = config
        self.llm = self.setup_llm()
        self.retriever = self.setup_retriever()
        self.rag_chain = self.setup_rag_chain()
        self.store = {}
    
    def setup_llm(self):
        """
        Sets up the ChatOllama model for the agent.

        Returns:
            ChatOllama: The initialized ChatOllama model.
        """
        local_llm = self.config["llm"]["model"]
        return ChatOllama(
            model=local_llm, 
            temperature=0,
        )
    
    def setup_retriever(self):
        """
        Sets up and returns a retriever object for vector retrieval.

        Returns:
            retriever: A retriever object for vector retrieval.
        """
        embedding_model = self.config["llm"]["embedding_model"]
        vector_store_path = self.config["rag"]["vector_store_path"]
        
        embedding_function = SentenceTransformerEmbeddings(model_name=embedding_model)
        vectorstore = Chroma(
            persist_directory=vector_store_path,
            embedding_function=embedding_function,
        )
        return vectorstore.as_retriever()
    
    def setup_rag_chain(self):
        """
        Sets up the RAG (Retrieval-Augmented Generation) chain for the AI agent.

        This method configures the RAG chain by defining the prompts and templates
        used for contextualizing questions and generating answers.

        Returns:
            The configured RAG chain.

        """
        contextualize_q_system_prompt = """Given a chat history and the latest user question \
        which might reference context in the chat history, formulate a standalone question \
        which can be understood without the chat history. Do NOT answer the question, \
        just reformulate it if needed and otherwise return it as is."""

        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        history_aware_retriever = create_history_aware_retriever(
            self.llm, self.retriever, contextualize_q_prompt
        )

        qa_system_prompt = """You are an assistant for question-answering tasks. \
        You are named 'NydasBot'. Use the following pieces of retrieved context to \
        answer the question. If you don't know the answer, just say that you don't know. \
        Use three sentences maximum and keep the answer concise.\n\n{context}"""

        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", qa_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        question_answer_chain = create_stuff_documents_chain(self.llm, qa_prompt)

        return create_retrieval_chain(history_aware_retriever, question_answer_chain)
    
    def get_session_history(self, session_id):
        """
        Retrieves the chat message history for a given session ID.

        If the session ID is not found in the store, a new ChatMessageHistory object is created
        and added to the store before returning it.

        Parameters:
        - session_id (str): The ID of the session for which to retrieve the chat message history.

        Returns:
        - ChatMessageHistory: The chat message history for the specified session ID.
        """
        if session_id not in self.store:
            self.store[session_id] = ChatMessageHistory()
        return self.store[session_id]
    
    def get_answer(self, input_text, session_id):
        """
        Retrieves an answer from the conversational RAG chain model based on the given input text and session ID.

        Args:
            input_text (str): The input text for generating the answer.
            session_id (str): The session ID for maintaining conversation history.

        Returns:
            str: The generated answer from the conversational RAG chain model.
        """
        conversational_rag_chain = RunnableWithMessageHistory(
            self.rag_chain,
            self.get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )
        
        return conversational_rag_chain.invoke(
            {"input": input_text},
            config={"configurable": {"session_id": session_id}}
        )["answer"]

class WebSocketServer:
    def __init__(self, host, port, model):
        self.host = host
        self.port = port
        self.model = model
    
    async def handle_connection(self, websocket, path):
            """
            Handles a WebSocket connection by receiving messages from the client,
            processing them using the AI model, and sending back the response.

            Parameters:
            - websocket: The WebSocket connection object.
            - path: The path of the WebSocket connection.

            Returns:
            None
            """
            async for message in websocket:
                try:
                    data = json.loads(message)
                    session_id = data.get("session_id", "default_session")
                    input_text = data["input"]

                    answer = self.model.get_answer(input_text, session_id)
                    
                    response = {"answer": answer}
                    await websocket.send(json.dumps(response))
                except Exception as e:
                    logging.error(f"An error occurred: {e}")
                    error_response = {"error": str(e)}
                    await websocket.send(json.dumps(error_response))
    
    async def start_server(self):
            """
            Starts the server and listens for incoming connections.

            This method uses the `websockets.serve` function to create a WebSocket server
            and binds it to the specified `host` and `port`. It then waits for incoming
            connections and handles each connection using the `handle_connection` method.

            Note: This method runs indefinitely until the program is terminated.

            Parameters:
                self (object): The instance of the class.

            Returns:
                None
            """
            async with websockets.serve(self.handle_connection, self.host, self.port):
                await asyncio.Future()  # run forever

if __name__ == "__main__":
    config_loader = ConfigLoader("parameters.toml")

    logging.basicConfig(level = config_loader.config["general"]["logging_level"])
    
    rag_model = RAGModel(config_loader.config)
    
    server = WebSocketServer("localhost", config_loader.config["general"]["port"], rag_model)
    
    asyncio.run(server.start_server())
