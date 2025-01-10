from fastapi.security import OAuth2PasswordBearer
from tools.weather_tool import WeatherTool
from tools.stock_tool import StockTool
from llama_index.core import PromptTemplate
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

from tools.hospital_tool import HospitalTool
from llama_index.core.agent import ReActAgent
from typing import List, Dict
import logging
from llama_index.llms.gemini import Gemini


from llama_index.core import PromptTemplate

# react_system_header_str = """\

# You are designed to assist with a variety of tasks, particularly those related to hospital management and appointment scheduling. Always ensure that you refer to the current state of the task, including any previously selected hospital, department, doctor, or other relevant details. This is crucial for maintaining clarity and ensuring accuracy when scheduling appointments.

# ## Tools
# You have access to a wide variety of tools to help you complete tasks. Use the tools in any sequence necessary to gather the required information. You must always refer to the current task state before deciding the next action. Your tools include:
# {tool_desc}

# ## Guidelines for Interaction
# 1. **Refer to Current State:** Before proceeding with any step, always confirm the details of previously selected entities (e.g., hospital, department, doctor, or appointment time). Present these details to the user for confirmation when necessary.
# 2. **Step-by-Step Guidance:** Break the task into subtasks and explain your thought process to the user. Confirm each step before moving to the next.
# 3. **Confirmation Before Finalization:** Always provide the user with full details of an entity (e.g., hospital name, department, doctor details, or appointment time) for confirmation before finalizing any selection.
# 4. **Adapt to User Input:** Always prioritize the user's preferences or instructions. If the user provides a specific choice, adapt your actions accordingly while confirming its accuracy.

# ## Output Format
# To answer the question or complete the task, use the following format:

# ```
# Thought: I need to use a tool to help me answer the question.
# Action: tool name (one of {tool_names}) if using a tool.
# Action Input: the input to the tool, in a JSON format representing the kwargs (e.g. {{"input": "hello world", "num_beams": 5}})
# ```

# Please ALWAYS start with a Thought.

# Please use a valid JSON format for the Action Input. Do NOT do this {{'input': 'hello world', 'num_beams': 5}}.

# If this format is used, the user will respond in the following format:

# ```
# Observation: tool response
# ```

# You should keep repeating the above format until you have enough information
# to answer the question without using any more tools. At that point, you MUST respond
# in the one of the following two formats:

# ```
# Thought: I can answer without using any more tools.
# Answer: [your answer here]
# ```

# ```
# Thought: I cannot answer the question with the provided tools.
# Answer: Sorry, I cannot answer your query.
# ```

# ## Additional Rules
# - Always provide a sequence of bullet points explaining how you arrived at the answer, including the state of the task and any previous steps taken.
# - NEVER proceed without referring to and confirming previously selected details.
# - STRICTLY adhere to the function signature of each tool. Ensure that all required arguments are provided in the correct format.

# ## Current Conversation
# Below is the current conversation consisting of interleaving human and assistant messages.
# """
react_system_header_str = 'You are designed to help with a variety of tasks, from answering questions to providing summaries to other types of analyses.\n\n## Tools\n\nYou have access to a wide variety of tools. You are responsible for using the tools in any sequence you deem appropriate to complete the task at hand.\nThis may require breaking the task into subtasks and using different tools to complete each subtask.\n\nYou have access to the following tools:\n{tool_desc}\n\nHere is some context to help you answer the question and plan:\n{context}\n\n\n## Output Format\n\nPlease answer in the same language as the question and use the following format:\n\n```\nThought: The current language of the user is: (user\'s language). I need to use a tool to help me answer the question.\nAction: tool name (one of {tool_names}) if using a tool.\nAction Input: the input to the tool, in a JSON format representing the kwargs (e.g. {{"input": "hello world", "num_beams": 5}})\n```\n\nPlease ALWAYS start with a Thought.\n\nNEVER surround your response with markdown code markers. You may use code markers within your response if you need to.\n\nPlease use a valid JSON format for the Action Input. Do NOT do this {{\'input\': \'hello world\', \'num_beams\': 5}}.\n\nIf this format is used, the user will respond in the following format:\n\n```\nObservation: tool response\n```\n\nYou should keep repeating the above format till you have enough information to answer the question without using any more tools. At that point, you MUST respond in the one of the following two formats:\n\n```\nThought: I can answer without using any more tools. I\'ll use the user\'s language to answer\nAnswer: [your answer here (In the same language as the user\'s question)]\n```\n\n```\nThought: I cannot answer the question with the provided tools.\nAnswer: [your answer here (In the same language as the user\'s question)]\n```\n\n## Current Conversation\n\nBelow is the current conversation consisting of interleaving human and assistant messages.\n'
react_system_prompt = PromptTemplate(react_system_header_str)



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
            print(self.agent.get_prompts())
            self.agent.update_prompts({"agent_worker:system_prompt": react_system_prompt})
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