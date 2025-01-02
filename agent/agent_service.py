from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .llm_service import LLMService
from .tools.weather_tool import WeatherTool
from .tools.stock_tool import StockTool
from .tools.user_tool import UserTool
from llama_index.core.agent import ReActAgent
from .auth_service import authenticate_user, create_access_token, verify_token
from llama_index.core.llms import ChatMessage
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class AgentService:
    def __init__(self):
        llm_service = LLMService()
        self.llm = llm_service.get_model()
        self.weather_tool = WeatherTool().tool
        self.stock_tool = StockTool().tool

        self.agent = ReActAgent.from_tools(
            tools=[self.weather_tool, self.stock_tool],
            llm=self.llm,
            verbose=True
        )

    def chat(self, query: str) -> str:
        response = self.agent.chat(query)
        return response.response

agent_service = AgentService()

from fastapi import HTTPException, Request, Depends
from jose import jwt, JWTError

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def get_current_user(request: Request):
    token = request.headers.get("Authorization")
    
    if not token:
        raise HTTPException(
            status_code=401, 
            detail="No token provided"
        )

    # Extract the token value, skipping "Bearer " prefix if present
    token = token.replace("Bearer ", "") if token.startswith("Bearer ") else token
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
