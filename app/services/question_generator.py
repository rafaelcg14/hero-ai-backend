import random
from uuid import uuid4
from openai import OpenAI

from app.models import MCQuestion

def generate_mc_questions(text_chunks):
    questions = []
    client = OpenAI()

    # Select a sample of 10 chunks or fewer
    chunks_sample = random.sample(text_chunks, min(len(text_chunks), 10))

    for chunk in chunks_sample:
        if len(chunk.page_content) > 20:
            try:
                prompt = f"""
                    Basándote en el siguiente fragmento del texto {chunk.page_content},

                    genera solo una pregunta de múltiple opciones con una única respuesta correcta.

                    Solo devuelve la pregunta, las opciones y la respuesta correcta.

                    En caso no puedas generar una pregunta, no devuelvas nada.
                """
                
                completion = client.beta.chat.completions.parse(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Eres un asistente que genera preguntas de múltiple opción basadas en el contenido de un documento con propósitos educativos."},
                        {"role": "user", "content": f"{prompt}"},
                    ],
                    response_format=MCQuestion
                )

                response = completion.choices[0].message.parsed

                # Store the question in the desired format
                question = {
                    "question_id": str(uuid4()),
                    "chunk_id": chunk.metadata["uuid"],
                    "question_dict": response,  # This contains the question and answer details
                    "reference_page": chunk.metadata.get("page", None)
                }

                questions.append(question)

            except Exception as e:
                # Handle errors during question generation
                print(f"Error while generating questions: {e}")
    
    return questions