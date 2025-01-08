from fastapi.security import OAuth2PasswordBearer
from tools.weather_tool import WeatherTool
from tools.stock_tool import StockTool

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

from tools.hospital_tool import HospitalTool
from llama_index.core.agent import ReActAgent
from typing import List, Dict
import logging
from llama_index.llms.gemini import Gemini

class AgentService:
    def __init__(self):
        # Initialize LLM service and get the model
        self.llm = Gemini(model="models/gemini-1.5-flash",api_key="AIzaSyDg9KyiwLv6w_oYP8mNSPbkXH0Syr-cvSk")
        
        # Initialize individual tools
        self.weather_tool = WeatherTool().tool
        self.stock_tool = StockTool().tool
        # self.user_tool = UserTool().tool
        
        # Initialize HospitalTool and its individual FunctionTools

        self.hospital_tool_instance = hospital_tool_instance = HospitalTool()
        self.hospital_tool_instance.set_token_provider(lambda: self.token)
        self.get_all_hospitals = hospital_tool_instance.get_all_hospitals
        self.search_hospitals = hospital_tool_instance.search_hospitals
        self.search_departments = hospital_tool_instance.search_departments
        self.search_doctors = hospital_tool_instance.search_doctors
        self.get_available_appointments = hospital_tool_instance.get_available_appointments
        self.create_appointment = hospital_tool_instance.create_appointment
        
        # List of all tools to be added to the agent
        self.tools = [
            self.weather_tool,
            self.stock_tool,
            # self.user_tool,
            self.get_all_hospitals,
            self.search_hospitals,
            self.search_departments,
            self.search_doctors,
            self.get_available_appointments,
            self.create_appointment
        ]
        
        self.base_prompt = ""
        self.chat_history: List[Dict[str, str]] = []
        self.max_history = 10
        self.agent = None  # Ensure each instance has its own agent
        self.token = None
        
    def set_base_prompt(self, prompt: str, token: str = None):
        """Set the base personality prompt for the agent, including the token"""
        if not prompt or not isinstance(prompt, str):
            raise ValueError("Invalid prompt format - must be non-empty string")
        
        if token:
            self.token = token
        
        # Combine base_prompt with token
        self.base_prompt = prompt.strip()
        self.context = f"{self.base_prompt}"
        
        print(f"Base prompt set: {self.base_prompt}")
        print(f"Context set with token: {self.context}")
        
        # Initialize agent with new context
        try:
            self.agent = ReActAgent.from_tools(
                tools=self.tools,
                llm=self.llm,
                verbose=True,
                system_message=self.base_prompt,
                context=self.context
            )
        except Exception as e:
            raise ValueError(f"Failed to initialize agent with new prompt: {str(e)}")
    
    def chat(self, query: str, token: str) -> str:
        print("DAO DUY DAT: ",self.agent)
        try:
            if not self.agent:
                print("Agent chưa được khởi tạo.")
                return "Agent chưa được khởi tạo."
            
            # In thông tin memory và chat history trước khi chat
            if hasattr(self.agent, 'memory'):
                print("Thông tin memory:")
                print(self.agent.memory)  # Hoặc self.agent.memory.state nếu cần chi tiết
            
            if hasattr(self.agent, 'chat_history'):
                print("Lịch sử chat hiện tại:")
                for msg in self.agent.chat_history:
                    print(f"{msg.role}: {msg.content}")
            if not query or not isinstance(query, str):
                raise ValueError("Invalid query format")

            # Set token to Agent
            self.token = token

            # Manage chat history
            if len(self.chat_history) >= self.max_history:
                self.chat_history = self.chat_history[-(self.max_history-1):]
            
            # Prepare messages
            messages = []
            if self.base_prompt:
                messages.append({"role": "system", "content": self.base_prompt})
            messages.extend(self.chat_history)
            
            # Add current query
            user_message = {"role": "user", "content": query}
            messages.append(user_message)
            
            # Get response from agent without passing the token
            response = self.agent.chat(query)
            
            # Update history
            self.chat_history.append(user_message)
            self.chat_history.append({"role": "assistant", "content": str(response)})
            
            return str(response)
            
        except Exception as e:
            logging.error(f"Chat error: {str(e)}")
            raise