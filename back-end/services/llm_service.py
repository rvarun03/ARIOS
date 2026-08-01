from core.paths import ENV_FILE

from dotenv import load_dotenv
from groq import Groq

import os

load_dotenv(ENV_FILE)

class LLM_Service:

    """
    Handles LLM answer generation using Groq.
    """

    def __init__(self):

        self.api_key = os.getenv("GROQ_API_KEY")
        self.model_name= os.getenv("GROQ_MODEL")

        if not self.api_key:
            raise RuntimeError(
                "GROQ_API_KEY is missing. Add it to back-end/.env"
            )

        self.client = Groq(
            api_key = self.api_key
        )

    def generate_answer(
        self,
        prompt
    ):

        response = self.client.chat.completions.create(

            model=self.model_name,
            messages=[
                {
                    "role":"system",
                    "content": (
                        "You are ARIOS, an AI research intelligence assistant. "
                        "Answer only using the provided context."
                    )
                },
                {
                    "role":"user",
                    "content":prompt
                }
            ],
            temperature=0.2

        )

        return response.choices[0].message.content
