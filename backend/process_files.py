#!/usr/bin/env python
import shutil
import os
import logging
import tomli
import warnings
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader

# Configuration
with open("parameters.toml", "rb") as params:
          config = tomli.load(params)

logging.basicConfig(level = config["general"]["logging_level"])
source_file_location = config["rag"]["source_file_location"]
processed_file_location = config["rag"]["processed_file_location"]
vector_store_path = config["rag"]["vector_store_path"]
embedding_model = config["llm"]["embedding_model"]
device = config["llm"]["device"]
batch_size = config["llm"]["batch_size"]

embed_model = HuggingFaceEmbeddings(
        model_name = embedding_model,
        model_kwargs = {"device": device},
        encode_kwargs = {"device": device, "batch_size": batch_size}
        )

warnings.filterwarnings("ignore")

def process_files():
    """
    Process files in a given directory.

    This function iterates over all the files in a specified directory and performs the following steps for each file:
    1. Loads the file using PyPDFLoader.
    2. Splits the loaded document into smaller chunks of text using RecursiveCharacterTextSplitter.
    3. Converts the text chunks into vector embeddings using an embed_model.
    4. Persists the vector embeddings to a specified directory using Chroma.
    5. Moves the processed file to a different location.

    If any exception occurs during the processing of a file, it will be logged as an error.

    Parameters:
    None

    Returns:
    None
    """
    files = [x for x in os.listdir(f"{source_file_location}")]

    for file in files:
        logging.info(file)
        try:
            loader = PyPDFLoader(f"{source_file_location}/{file}", extract_images=True)
            data = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            all_splits = text_splitter.split_documents(data)
            Chroma.from_documents(documents=all_splits, embedding=embed_model, persist_directory=vector_store_path)
            logging.info(f"{file} processed.")
            shutil.move(os.path.join(f"{source_file_location}", file), f"{processed_file_location}")

        except Exception as e:
            logging.error(e)

if __name__ == "__main__":
    process_files()
