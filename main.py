import openai
import random
import time
import anthropic
from openai import OpenAI
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models
import os


gpt_key = ""
claude_key = ""
# Set up your OpenAI API key
gpt_client = OpenAI(api_key=gpt_key)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "hallowed-spider-383508-0fcae3cd5cf8.json"
vertexai.init(project="hallowed-spider-383508", location="us-central1")



template_prompt = "You are playing a game to determine who the human is among participants. Do not at any point imply that you are an AI before you're deciding who is the human. Once you are deciding who is the human, that's the time you admit that you are an AI. Answers should be at maximum four sentences."

def get_random_question():
    prompt1 = "Generate a random question for a conversation. Keep in mind that these questions are to test if the player is a human or not. Make it an open-ended question:"
    response =  gpt_client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt1
    )
    return response.choices[0].text.strip()

def get_gpt4_response(prompt, chat_history):
    messages = chat_history + [{"role": "user", "content": prompt}]
    response = gpt_client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=50
    )
    # Append the new response to chat history (if needed outside this function)
    chat_history.append({"role": "user", "content": response.choices[0].message.content})
    
    return response.choices[0].message.content


def get_claude_response(prompt, chat_history):
    claude_client = anthropic.Anthropic(api_key=claude_key)
    full_prompt = f"{chat_history} User: {prompt} AI:"
    response = claude_client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        temperature=1,
        system=template_prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": full_prompt
                    }
                ]
            }
        ]
    )
    return response.content[0].text

def get_gemini_response(prompt, chat_history):
    full_prompt = f"{template_prompt} {chat_history} User: {prompt} AI:"
    model = GenerativeModel("gemini-1.0-pro-002")
    response = model.generate_content([full_prompt], generation_config={"max_output_tokens": 300, "temperature": 1, "top_p": 1})
    return response.text

def run_game():
    models = {
        "GPT-4": get_gpt4_response,
        "Claude 3": get_claude_response,
        "Gemini 1.0": get_gemini_response
    }
    chat_history = []

    print("Welcome to the Reverse Turing Game!")
    print("There are three AI models and one human in this conversation. The goal is to decide which one is the human!\n")

    # Initialize the game context in chat history
    chat_history.append({"role": "system", "content": template_prompt})

    for i in range(3):
        question = get_random_question()
        print(f"Round {i+1}, Question: {question}\n")

        # Append question to chat history
        chat_history.append({"role": "user", "content": question})

        for model_name, get_response in models.items():
            response = get_response(question, chat_history)
            print(f"{model_name}: {response}")

            # Append each model's response to chat history
            chat_history.append({"role": "user", "content": f"{model_name}: {response}"})
            time.sleep(1)

        user_response = input("Your response: ")
        chat_history.append({"role": "user", "content": f"LLM Hume: {user_response}"})
        print("\n")

    print("Now it's time to guess who the human is.\n")
    for model_name, get_response in models.items():
        guess = get_response("Who do you think the human is?", chat_history)
        print(f"{model_name} guesses: {guess}")
        chat_history.append({"role": "user", "content": f"{model_name} guesses: {guess}"})
        time.sleep(1)

    print("The game has ended. Thank you for playing!")


if __name__ == "__main__":
    run_game()