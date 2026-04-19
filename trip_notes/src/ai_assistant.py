from dotenv import load_dotenv, find_dotenv
import os
import openai
from openai import OpenAI
from src.rag import search_guides

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


def rag_ask(question: str) -> str:
    chunks = search_guides(question, n_results=3)

    if not chunks:
        return "No guides found. Add .txt, .md, or .pdf files to guides/ and press [R] to rebuild the index."

    context = "\n\n---\n\n".join(chunks)

    rag_system_prompt = (
        f"You are a travel assistant with access to the user's personal travel guides.\n"
        f"Use the context below as your PRIMARY source. If the context contains relevant\n"
        f"information, use it in your answer. If the context is insufficient, you may\n"
        f"supplement with general knowledge but clearly indicate what comes from the guides\n"
        f"and what is general advice. If the context has nothing relevant at all, say:\n"
        f"I don't have specific guide information about that.\n\n"
        f"Context from your travel guides:\n"
        f"{context}"
    )

    return ask(question, system_prompt=rag_system_prompt, max_tokens=2048)


def generate_trip_briefing(city: str, country: str, notes: list = None) -> dict | None:
    base = (
        f"Give a 3-sentence travel overview of {city}, {country}. "
        "Cover: what it's like to visit, best season to go, and one must-see attraction."
    )

    if notes is not None and len(notes) > 0:
        notes_text = "\n".join(f"- {n}" for n in notes)
        overview_prompt = base + f"\n\nPersonal notes about this trip:\n{notes_text}"
    else:
        overview_prompt = base

    overview = ask(overview_prompt, system_prompt=TRAVEL_SYSTEM_PROMPT)
    if overview is None:
        return None

    packing_prompt = (
        f"Based on this destination overview:\n{overview}\n\n"
        f"Write a 5-item packing list specific to {city}."
    )
    packing_list = ask(packing_prompt, system_prompt=TRAVEL_SYSTEM_PROMPT)
    if packing_list is None:
        return None

    return {"overview": overview, "packing_list": packing_list}


if __name__ == "__main__":
    result = generate_trip_briefing("Tokyo", "Japan")
    if result:
        print("Overview:", result["overview"])
        print("Packing list:", result["packing_list"])
