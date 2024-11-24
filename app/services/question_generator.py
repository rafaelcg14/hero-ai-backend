import random
from uuid import uuid4
from openai import OpenAI

from app.models import MCQuestion

def generate_mc_questions(text_chunks):
    questions = []
    topics = []
    client = OpenAI()

    # Select a sample of 10 chunks or fewer
    chunks_sample = random.sample(text_chunks, min(len(text_chunks), 10))

    for chunk in chunks_sample:
        if len(chunk.page_content) > 20:
            try:
                prompt = f"""
                    Basándote en el siguiente fragmento del texto {chunk.page_content},

                    genera solo una pregunta de múltiple opciones con una única respuesta correcta.

                    Solo devuelve la pregunta, las opciones con un índice antecedido 
                    
                    (por ejemplo "A)", "B)", "C), "D)") y la respuesta correcta debe ser
                    
                    exactamente igual a una de las opciones.

                    En caso no puedas generar una pregunta, no devuelvas nada.
                """

                topic_prompt = f"""
                    Basándote en el siguiente fragmento del texto: {chunk.page_content},

                    determina el tema principal o tema del contenido.

                    Devuelve el tema en una sola oración que tenga sujeto y predicado.

                    Si no puedes determinar el tema, no devuelvas nada.
                """
                
                # Call the OpenAI API for the question
                question_completion = client.beta.chat.completions.parse(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Eres un asistente que genera preguntas de múltiple opción basadas en el contenido de un documento con propósitos educativos."},
                        {"role": "user", "content": f"{prompt}"},
                    ],
                    response_format=MCQuestion
                )

                question_response = question_completion.choices[0].message.parsed

                # Store the question in the desired format
                question = {
                    "question_id": str(uuid4()),
                    "chunk_id": chunk.metadata["uuid"],
                    "question_dict": question_response,  # This contains the question and answer details
                    "reference_page": chunk.metadata.get("page", None)
                }

                # Call the OpenAI API for the topic
                topic_completion = client.beta.chat.completions.parse(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Eres un asistente que extrae temas principales de un fragmento de texto."},
                        {"role": "user", "content": f"{topic_prompt}"},
                    ]
                )

                topic_response = topic_completion.choices[0].message.content.strip()

                topics.append({
                    "chunk_id": chunk.metadata["uuid"],
                    "topic": topic_response
                })



                questions.append(question)

            except Exception as e:
                # Handle errors during question generation
                print(f"Error while generating questions: {e}")
    
    return {"questions": questions, "topics": topics}