import requests
from typing import Union

class HospitalAPI:
    def get_all_hospitals_fn(self, token: str) -> Union[str, dict]:
        try:
            url = "http://127.0.0.1:8000/api/hospitals/"
            headers = {
                'Authorization': f'Bearer {token}'
            }
            
            print(f"Gửi yêu cầu GET đến {url}")
            
            response = requests.get(url, headers=headers, timeout=3000)
            
            # In phản hồi HTTP
            print("Mã trạng thái:", response.status_code)
            print("Nội dung phản hồi:", response.text)
            
            # Kiểm tra lỗi
            response.raise_for_status()
            
            # Phân tích JSON phản hồi
            hospitals = response.json()
            
            # Chuyển đổi danh sách bệnh viện thành chuỗi dễ đọc
            hospital_list = "\n".join(
                [f"ID: {h['hospital_id']}, Tên: {h['hospital_name']}, Địa chỉ: {h['hospital_address']}" for h in hospitals]
            )

            return hospital_list
        except requests.exceptions.RequestException as e:
            return f"Lỗi khi gửi yêu cầu: {str(e)}"

# Thử nghiệm hàm
if __name__ == "__main__":
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBleGFtcGxlLmNvbSIsImV4cCI6MTczNjE1NjAxOH0.9QWhRvkQSiey5DVpMwPdGUIGsHTLaLm_xVcH4o1djtc"
    hospital_api = HospitalAPI()
    result = hospital_api.get_all_hospitals_fn(token)
    print("Kết quả:\n", result)