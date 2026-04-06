from dotenv import load_dotenv, find_dotenv
import os
import openai
from openai import OpenAI

load_dotenv(find_dotenv())

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)
MODEL = "openrouter/free"

TRAVEL_SYSTEM_PROMPT = (
    "You are a knowledgeable, concise travel assistant focused on practical, "
    "budget-friendly advice for student travelers. Keep answers under 200 words. "
    "Be specific and name places, neighborhoods, routes, and timing recommendations "
    "instead of general advice."
)


def ask(user_message, system_prompt=None, temperature=0.7, max_tokens=500) -> str | None:
    messages = []

    if system_prompt is not None:
        messages.append({"role": "system", "content": system_prompt})

    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=30,
        )
        return response.choices[0].message.content
    except openai.AuthenticationError:
        print("Authentication failed. Please check your OPENROUTER_API_KEY.")
        return None
    except openai.RateLimitError:
        print("Rate limit reached. Please try again in a moment.")
        return None
    except openai.APIConnectionError:
        print("Could not connect to the API. Please check your internet connection.")
        return None


if __name__ == "__main__":
    result = ask(
        "What is the best time of year to visit Japan?",
        system_prompt=TRAVEL_SYSTEM_PROMPT,
    )
    print(result)
