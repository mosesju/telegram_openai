import re
import logging
from pydantic import BaseModel

def extract_sentence(obj, num_sentences=5):
    sentence = obj["sentence"]
    text = obj["text"]
    item = obj["item"]
    similarity = obj["similarity"]
    id_val = obj["id"]

    sentences = re.split(r'(?<=[.!?])\s+', text)

    try:
        target_index = sentences.index(sentence)
    except ValueError:
        return []
    start = max(0, target_index - num_sentences // 2)
    end = min(len(sentences), start + num_sentences)
    start = max(0, end - num_sentences)
    extracted_text = ' '.join(sentences[start:end])
    logging.info(f"TRIMMED SUPABASE RESPONSE: {extracted_text}")
    return extracted_text

# Too much to do with async stuff here
# class Questions(BaseModel):
#     question1: str
#     question2: str
#     question3: str

# def question_suggestion(client, messages):
#     response = client.chat.completions.create(
#         model="gpt-3.5-turbo",
#         response_model=Questions,
#         messages=messages
#     )
#     logging.info(f"RESPONSE: {response}")   
#     return response