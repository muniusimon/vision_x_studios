# openai.py (Mock Module)

class ChatCompletion:
    def create(self, model, messages):
        # This is a mock response for local testing
        system_message = [msg['content'] for msg in messages if msg['role'] == 'system'][0]
        user_message = [msg['content'] for msg in messages if msg['role'] == 'user'][0]

        # This is a simulated response from the "GPT" model
        return {
            "model": model,
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": f"This is a simulated response to: '{user_message}'"
                    }
                }
            ]
        }

class OpenAI:
    def __init__(self):
        self.chat = ChatCompletion()

# Instantiate OpenAI client
client = OpenAI()
