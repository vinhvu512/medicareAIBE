from llama_index.core.tools import FunctionTool

class StockTool:
    def __init__(self):
        self.tool = FunctionTool.from_defaults(
            fn=self.get_stock_price,
            description="Lấy giá cổ phiếu theo mã. Truyền vào 'stock' là mã cổ phiếu."
        )

    def get_stock_price(self, stock: str) -> str:
        return f"Giá cổ phiếu {stock} hiện tại là 120 USD."
