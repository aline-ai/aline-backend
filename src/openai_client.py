from os import environ
import openai

from dotenv import load_dotenv
load_dotenv()

openai.api_key = environ.get("OPENAI_API_KEY")

prompt = "Rephrase and restructure the sentence below to make it more fluent: $sentence"

def get_edits(sentence, prompt=prompt, engine="text-davinci-003", max_tokens=0, **kwargs) -> list:
    if not max_tokens:
        max_tokens = int((sentence.count(" ") + 1) * 3) # Max tokens is 3x the number of words in the sentence
    completion = openai.Completion.create(
        engine=engine, 
        prompt=prompt.replace("$sentence", sentence), 
        max_tokens=max_tokens,
        **kwargs
    )
    return completion.choices
