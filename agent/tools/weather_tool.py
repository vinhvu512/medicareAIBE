from llama_index.core.tools import FunctionTool

class WeatherTool:
    def __init__(self):
        self.tool = FunctionTool.from_defaults(
            fn=self.get_weather,
            description="Lấy thông tin thời tiết hiện tại cho một thành phố. Truyền vào 'location' là tên thành phố."
        )

    def get_weather(self, location: str) -> str:
        return f"Thời tiết tại {location} là 30°C, trời đẹp."
