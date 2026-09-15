# Hero AI Backend

This is the backend for the Hero AI project, built using FastAPI.

## Features

- FastAPI for building APIs quickly and efficiently
- Asynchronous request handling
- Automatic interactive API documentation with Swagger UI and ReDoc
- Easy integration with databases and other services

## Requirements

- Python 3.7+
- FastAPI
- Uvicorn

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/rafaelcg14/hero-ai-backend.git
    cd hero-ai-backend
    ```

2. Create and activate a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Environment Variables

Create a `.env` file in the project root with:

```
OPENAI_API_KEY=your-openai-key
DEEPSEEK_API_KEY=your-deepseek-key
```

`OPENAI_API_KEY` powers PDF processing, question generation, and the `/chat/` endpoint. `DEEPSEEK_API_KEY` powers `/chat-test/`, a second chat endpoint over the same document context but backed by DeepSeek (`deepseek-reasoner`) instead of OpenAI.

## Running the Application

1. Start the FastAPI server using Uvicorn:

    ```bash
    uvicorn main:app --reload
    ```

2. Open your browser and navigate to `http://127.0.0.1:8000` to access the API documentation.


## Contact

For any inquiries, please contact [your-email@example.com].
