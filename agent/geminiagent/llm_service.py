from llama_index.llms.gemini import Gemini

class LLMService:
    def __init__(self):
        self.llm = Gemini(model="models/gemini-1.5-flash",api_key="AIzaSyDg9KyiwLv6w_oYP8mNSPbkXH0Syr-cvSk")

    def get_model(self):
        return self.llm
