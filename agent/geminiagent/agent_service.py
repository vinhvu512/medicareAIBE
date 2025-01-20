from fastapi.security import OAuth2PasswordBearer
from tools.weather_tool import WeatherTool
from tools.stock_tool import StockTool
from llama_index.core import PromptTemplate
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

from tools.hospital_tool import HospitalTool
from tools.map_tool import MapTool
from llama_index.core.agent import ReActAgent
from typing import List, Dict
import logging
from llama_index.llms.gemini import Gemini


from llama_index.core import PromptTemplate

import nest_asyncio
nest_asyncio.apply()

react_system_header_str = 'You are designed to help with a variety of tasks, from answering questions to providing summaries to other types of analyses.\n\n## Tools\n\nYou have access to a wide variety of tools. You are responsible for using the tools in any sequence you deem appropriate to complete the task at hand.\nThis may require breaking the task into subtasks and using different tools to complete each subtask.\n\nYou have access to the following tools:\n{tool_desc}\n\nHere is some context to help you answer the question and plan:\n{context}\n\n\n## Output Format\n\nPlease answer in the same language as the question and use the following format:\n\n```\nThought: The current language of the user is: (user\'s language). I need to use a tool to help me answer the question.\nAction: tool name (one of {tool_names}) if using a tool.\nAction Input: the input to the tool, in a JSON format representing the kwargs (e.g. {{"input": "hello world", "num_beams": 5}})\n```\n\nPlease ALWAYS start with a Thought.\n\nNEVER surround your response with markdown code markers. You may use code markers within your response if you need to.\n\nPlease use a valid JSON format for the Action Input. Do NOT do this {{\'input\': \'hello world\', \'num_beams\': 5}}.\n\nIf this format is used, the user will respond in the following format:\n\n```\nObservation: tool response\n```\n\nYou should keep repeating the above format till you have enough information to answer the question without using any more tools. At that point, you MUST respond in the one of the following two formats:\n\n```\nThought: I can answer without using any more tools. I\'ll use the user\'s language to answer\nAnswer: [your answer here (In the same language as the user\'s question)]\n```\n\n```\nThought: I cannot answer the question with the provided tools.\nAnswer: [your answer here (In the same language as the user\'s question)]\n```\n\n## Current Conversation\n\nBelow is the current conversation consisting of interleaving human and assistant messages.\n'
react_system_prompt = PromptTemplate(react_system_header_str)

class AgentService:
    def __init__(self, agent_id: int, user_id: str, websocket_manager=None):
        # Add agent_id property
        self.agent_id = agent_id
        self.user_id = user_id
        self.websocket_manager = websocket_manager

        # Initialize LLM service and get the model
        self.llm = Gemini(model="models/gemini-1.5-flash",api_key="AIzaSyDg9KyiwLv6w_oYP8mNSPbkXH0Syr-cvSk")
        
        # Initialize HospitalTool and its individual FunctionTools
        self.hospital_tool_instance = hospital_tool_instance = HospitalTool()
        self.hospital_tool_instance.set_token_provider(lambda: self.token)
        self.get_all_hospitals = hospital_tool_instance.get_all_hospitals
        self.search_hospitals = hospital_tool_instance.search_hospitals
        self.search_departments = hospital_tool_instance.search_departments
        self.search_doctors = hospital_tool_instance.search_doctors
        self.get_available_appointments = hospital_tool_instance.get_available_appointments
        self.create_appointment = hospital_tool_instance.create_appointment
        


        # Tool for mapbox
        self.map_tool_instance = MapTool(
            user_id=self.user_id, 
            websocket_manager=self.websocket_manager
        )
        self.search_locations = self.map_tool_instance.search_locations
        self.get_place_details = self.map_tool_instance.get_place_details
        self.get_route = self.map_tool_instance.get_route


        self.predict_disease = hospital_tool_instance.predict_disease
        self.create_health_report_tool = hospital_tool_instance.create_health_report_tool
        # List of all tools to be added to the agent
        self.tools = [
            self.get_all_hospitals,
            self.search_hospitals,
            self.search_departments,
            self.search_doctors,
            self.get_available_appointments,
            self.create_appointment,
            self.predict_disease,
            self.create_health_report_tool,



            self.search_locations,
            self.get_place_details,
            self.get_route
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
                context=self.context,
                # tool_executor_mapping={"get_route_fn": self.map_tool_instance.get_route_fn}
                tool_executor_mapping={"get_route_fn": self.map_tool_instance.get_route_fn}
            )
            print(self.agent.get_prompts())
            self.agent.update_prompts({"agent_worker:system_prompt": react_system_prompt})
        except Exception as e:
            raise ValueError(f"Failed to initialize agent with new prompt: {str(e)}")
    
    def chat(self, query: str, token: str) -> str:
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