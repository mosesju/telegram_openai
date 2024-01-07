async def generate_response_3_5_turbo(client, messages):
    """Generate a response from OpenAI."""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response.choices[0].message.content

async def get_embedding(client, query):
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=query,
        encoding_format="float"
    )
    if response and response.data:
        embedding = response.data[0].embedding
        return embedding