import asyncio
from pathlib import Path
import threading
from langchain.llms import OpenAI
from llama_index import SimpleDirectoryReader, ServiceContext, VectorStoreIndex
from llama_index import set_global_service_context
from llama_index.response.pprint_utils import pprint_response
from llama_index.tools import QueryEngineTool, ToolMetadata
from llama_index.query_engine import SubQuestionQueryEngine
import os
import pickle
import gradio as gr
import glob
from dotenv import load_dotenv
import os

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")


# Constants for API keys
class Config:
    base_url = "https://api.openai.com/v1/"
    api_key = openai_api_key
    model = "gpt-3.5-turbo"
    vectorstore_filename = 'none'
    pdf_folder = 'pdf_input'
    vectorstore_folder = 'vector_databases'


class chatlogic:
    def __init__(self):
        self.config = Config()
        self.setup_folders()
        os.environ['OPENAI_API_KEY'] = self.config.api_key
        llm = OpenAI(base_url=self.config.base_url, api_key=self.config.api_key)
        service_context = ServiceContext.from_defaults(llm=llm)
        set_global_service_context(service_context=service_context)
        self.vectorstore_status_label = None
        self.pdf_engine = None
        self.initialize_vectorstore()

    def setup_folders(self):
        if not os.path.exists(self.config.pdf_folder):
            os.makedirs(self.config.pdf_folder)
            print(f"Created folder: {self.config.pdf_folder}")

        if not os.path.exists(self.config.vectorstore_folder):
            os.makedirs(self.config.vectorstore_folder)
            print(f"Created folder: {self.config.vectorstore_folder}")

    def save_vectorstore_to_file(self, vectorstore):
        print(">save vectorstore to file")
        full_path = os.path.join(self.config.vectorstore_folder, self.config.vectorstore_filename)
        print("vectorstore filename to save: " + self.config.vectorstore_filename)
        with open(full_path, 'wb') as file:
            pickle.dump(vectorstore, file)
        print(f"VectorStore saved to {full_path}")
        self.vectorstore_status_label = "Vector store Updated."

    def load_vectorstore_from_file(self):
        print(">load vectorstore from file")

        full_path = os.path.join(self.config.vectorstore_folder, self.config.vectorstore_filename)
        self.vectorstore_status_label = "Vector store from disk. {}".format(self.config.vectorstore_filename)
        with open(full_path, 'rb') as file:
            return pickle.load(file)

    def initialize_vectorstore(self):
        print(">initialize vectorstore")
        filename = glob.glob(os.path.join(self.config.pdf_folder, '*.pdf'))[0]
        # Check if VectorStore exists
        if os.path.exists(os.path.join(self.config.vectorstore_folder, self.config.vectorstore_filename)):
            print("Loading existing VectorStore from file. {}".format(self.config.vectorstore_filename))
            self.pdf_engine = self.load_vectorstore_from_file()
        else:
            # Check for existing PDFs in the PDF folder
            pdf_files = glob.glob(os.path.join(self.config.pdf_folder, '*.pdf'))
            if pdf_files:
                print(f"Found existing PDF while initializing vectorstore: {pdf_files[0]}")
                filename = pdf_files[0]  # Use the first found PDF file
            else:
                print("Warning: No PDF files found in the PDF folder.")
                # If no PDFs found, also update the label
                self.vectorstore_status_label = "None"
                return None  # Or handle this scenario as needed
            # self.create_and_save_vectorstore(filename)
            fn = os.path.splitext(os.path.basename(filename))[0]
            self.config.vectorstore_filename = fn + ".pkl"
            if os.path.exists(os.path.join(self.config.vectorstore_folder, self.config.vectorstore_filename)):
                self.pdf_engine = self.load_vectorstore_from_file()
            else:
                print("Warning: No vectorstore file found for this PDF.")

    def create_and_save_vectorstore(self, filename):
        print(">create and save vectorstore")
        if filename:
            print(filename)
            fn = os.path.splitext(os.path.basename(filename))[0]
            self.config.vectorstore_filename = fn + ".pkl"
            print("new vectorstore filename {}".format(self.config.vectorstore_filename))

            if not os.path.exists(os.path.join(self.config.vectorstore_folder, self.config.vectorstore_filename)):
                pdf_docs = SimpleDirectoryReader(input_files=[filename]).load_data()
                pdf_index = VectorStoreIndex.from_documents(pdf_docs)
                self.pdf_engine = pdf_index.as_query_engine(similarity_top_k=3)
                self.save_vectorstore_to_file(self.pdf_engine)
            else:
                print("vector store already exists, skipping.")
                self.pdf_engine = self.load_vectorstore_from_file()
                self.vectorstore_status_label = "Vector store loaded from disk."
        else:
            print("Warning: Vectorstore not created.")

    def query_document(self, query):
        print(f"Sending query: {query}")
        response = self.pdf_engine.query(query)  # Assuming timeout is supported
        print(f"Received response: {response}")
        return response


def gradio_query_document(query, chat_logic_instance):
    # Correctly call the query_document function on the chat_logic_instance
    return (chat_logic_instance.query_document(query))


def gradio_process_pdf(file, chat_logic_instance):
    # Save the uploaded file in the designated PDF folder and update the vector store
    filename = file.orig_name
    chat_logic_instance.create_and_save_vectorstore(filename)
    return "{}".format(os.path.basename(filename))


def main(chat_logic_instance):
    print(chat_logic_instance.vectorstore_status_label)

    # Gradio Interface
    with gr.Blocks() as app:
        gr.Markdown("<center><h1>GPT PDF Chat</h1></center>")
        with gr.Row():
            with gr.Column(scale=4):
                question_input = gr.Textbox(label="Enter your question")
                answer_button = gr.Button("Get Answer")
                answer_output = gr.Textbox(label="Answer", lines=10)

            with gr.Column(scale=1):
                pdf_upload = gr.File(label="Ingest PDF File", type="file")
                pdf_process_button = gr.Button("Process PDF")
                pdf_status_label = gr.Label("No PDF Loaded")
                vectorstore_status_label = gr.Label(chat_logic_instance.vectorstore_status_label, interactive=True)
                dark_mode_btn = gr.Button("Dark Mode")

        # Bind functions to Gradio interface
        answer_button.click(
            fn=lambda query: gradio_query_document(query, chat_logic_instance),
            inputs=question_input,
            outputs=answer_output
        )

        pdf_process_button.click(
            fn=lambda file: gradio_process_pdf(file, chat_logic_instance),
            inputs=pdf_upload,
            outputs=pdf_status_label,
        )

        dark_mode_btn.click(
            None,
            None,
            None,
            _js="""() => {
                    if (document.querySelectorAll('.dark').length) {
                        document.querySelectorAll('.dark').forEach(el => el.classList.remove('dark'));
                    } else {
                        document.querySelector('body').classList.add('dark');
                    }
                }""",
        )

    app.launch()


if __name__ == "__main__":
    chat_logic_instance = chatlogic()
    main(chat_logic_instance)
