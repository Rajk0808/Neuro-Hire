import os

from chromadb.api.types import EmbeddingFunction

class QwenMultimodalEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: list[str]) -> list[list[float]]:
        res = []
        for text in input:
            res.append(get_embeddings(text))
        return res
    
from dotenv import load_dotenv
load_dotenv()
import requests
import json


def get_embeddings(input_text):
    response = requests.post(
      url="https://openrouter.ai/api/v1/embeddings",
      headers={
        "Authorization": f"Bearer {OPENROUTER_API_KEY}" if (OPENROUTER_API_KEY := os.getenv("OPENROUTER_API_KEY")) else "",
        "Content-Type": "application/json"
        },
      data=json.dumps({
        "model": "nvidia/llama-nemotron-embed-vl-1b-v2:free",
        "input": [
          {
            "content": [
              {"type": "text", "text": input_text}
            ]
          }
        ],
        "encoding_format": "float",
        "dimensions": 384
      })
    )
    return response.json()['data'][0]['embedding']