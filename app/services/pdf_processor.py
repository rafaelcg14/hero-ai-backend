import requests
from io import BytesIO
from uuid import uuid4
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain_community.document_loaders import PyPDFLoader
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

from app.services.question_generator import generate_mc_questions
from app.services.summary_generator import generate_summary_from_topics

def process_pdf(pdf_url: str):
    
    load_dotenv()

    # Download PDF into memory
    response = requests.get(pdf_url, stream=True)
    if response.status_code != 200:
        raise ValueError("Failed to download the PDF.")

    pdf_stream = BytesIO()
    for chunk in response.iter_content(chunk_size=8192):
        pdf_stream.write(chunk)
    
    pdf_stream.seek(0)  # Reset the stream position to the beginning

    # Extract text using PyPDF2
    pdf_reader = PdfReader(pdf_stream)
    docs = []
    for page_num, page in enumerate(pdf_reader.pages):
        text = page.extract_text()
        if text:
            docs.append(Document(page_content=text, metadata={"page": page_num + 1}))

    # Split PDF text in chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len)
    text_chunks = text_splitter.split_documents(docs)

     # Step 4: Create a vector store
    uuids = [str(uuid4()) for _ in range(len(text_chunks))]
    for chunk, uuid in zip(text_chunks, uuids):
        chunk.metadata["uuid"] = uuid

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_store = FAISS.from_documents(documents=text_chunks, embedding=embeddings, ids=uuids)

    # Initialize the chatbot
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(llm, retriever=vector_store.as_retriever(), memory=memory)

    # Generate multiple-choice questions
    generation_results = generate_mc_questions(text_chunks)
    questions = generation_results["questions"]

    # Generate a summary of the document considering each topic
    topics = generation_results["topics"]
    topics_text = " ".join([topic["topic"] for topic in topics])
    summary = generate_summary_from_topics(topics_text)
        


    return questions, summary, conversation_chain