import requests
from uuid import uuid4
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

from app.services.question_generator import generate_mc_questions

def process_pdf(pdf_url: str):
    
    load_dotenv()

    # Download PDF
    temp_file_path = "temp_url.pdf"
    response = requests.get(pdf_url, stream=True)
    if response.status_code != 200:
        raise ValueError("Failed to download the PDF.")

    with open(temp_file_path, "wb") as temp_file:
        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)
    
    # Extract text from the PDF
    loader = PyPDFLoader(temp_file_path)
    docs = loader.load()

    # Split PDF text in chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len)
    text_chunks = text_splitter.split_documents(docs)

     # Step 4: Create a vector store
    uuids = [str(uuid4()) for _ in range(len(text_chunks))]
    for chunk, uuid in zip(text_chunks, uuids):
        chunk.metadata["uuid"] = uuid

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_store = FAISS.from_documents(documents=text_chunks, embedding=embeddings, ids=uuids)

    # Initialize the chatboy
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(llm, retriever=vector_store.as_retriever(), memory=memory)

    # Generate multiple-choice questions
    questions = generate_mc_questions(text_chunks)

    return questions, conversation_chain