from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

# Create a new chat bot
chatbot = ChatBot('MyBot')

# Create a new trainer for the chatbot
trainer = ChatterBotCorpusTrainer(chatbot)

# Train the chatbot on English language data
trainer.train('chatterbot.corpus.english')

def get_chatterbot_response(user_input):
    # Get a response from the chatbot
    response = chatbot.get_response(user_input)
    return str(response)

def handle_response(text: str) -> str:
    # Create your own response logic
    processed: str = text.lower()

    return get_chatterbot_response(processed)


#below code is to integrate chat gpt 
# import openai

# # Set up your OpenAI API key
# openai.api_key = 'YOUR_OPENAI_API_KEY'  # Replace with your actual API key

# def get_chatgpt_response(user_input):
#     # Use OpenAI GPT to generate a response
#     response = openai.Completion.create(
#         engine="text-davinci-003",  # Choose the appropriate engine
#         prompt=user_input,
#         max_tokens=50  # Adjust as needed
#     )

#     return response.choices[0].text.strip()

# def handle_response(text: str) -> str:
#     # Create your own response logic
#     processed = text.lower()

#     # Use ChatGPT for generating responses
#     return get_chatgpt_response(processed)