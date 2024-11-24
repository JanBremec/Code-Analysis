from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Access the API_KEY
API_KEY = os.getenv("HUGGINGFACE_API_KEY")

if not API_KEY:
    raise ValueError("API_KEY is missing! Please set it in the .env file.")


def getFunctionExplanation(function):
    client = InferenceClient(api_key=API_KEY)

    messages = [
        {
            "role": "user",
            "content": f"What does this do: {function}"
        }
    ]

    completion = client.chat.completions.create(
        model="Qwen/Qwen2.5-Coder-32B-Instruct",
        messages=messages,
        max_tokens=1000
    )


    return completion.choices[0].message


def getCodeImprovements(code):
    client = InferenceClient(api_key=API_KEY)

    messages = [
        {
            "role": "user",
            "content": f"What can i improve in this code and how: {code}"
        }
    ]

    completion = client.chat.completions.create(
        model="Qwen/Qwen2.5-Coder-32B-Instruct",
        messages=messages,
        max_tokens=1000
    )

    return completion.choices[0].message


def getQuestionAnswered(code, question):
    client = InferenceClient(api_key=API_KEY)

    messages = [
        {
            "role": "user",
            "content": f"This is the code: ({code}) and i want to know: ({question})"
        }
    ]

    completion = client.chat.completions.create(
        model="Qwen/Qwen2.5-Coder-32B-Instruct",
        messages=messages,
        max_tokens=1000
    )

    return completion.choices[0].message