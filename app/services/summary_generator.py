from openai import OpenAI


def generate_summary_from_topics(topics_text):
    client = OpenAI()

    prompt = f"""
    Basándote en los siguientes temas extraídos de un documento:
    
    {topics_text}

    Genera un resumen conciso y claro de estos temas en un solo párrafo.
    """
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un asistente que genera resúmenes claros y concisos de temas."},
                {"role": "user", "content": prompt},
            ]
        )
        summary = completion.choices[0].message.content
        
        return summary
    
    except Exception as e:
        print(f"Error generating summary: {e}")
        return "No summary could be generated."
