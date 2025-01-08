# from llama_index.core.tools import FunctionTool
# from sqlalchemy.orm import Session
# from database.session import SessionLocal
# from schemas.appointment import AppointmentCreate
# from models.hospital import Hospital
# from models.department import Department
# from models.doctor import Doctor
# from models.appointment import Appointment
# from typing import List
import requests
class HospitalTool:import requests
from llama_index.core.tools import FunctionTool
from typing import List, Union
# from llama_index.tools.requests import RequestsToolSpec

BASE_URL = "http://localhost:80/api"

class HospitalTool:
    def __init__(self):
        self.get_all_hospitals = FunctionTool.from_defaults(
            fn=self.get_all_hospitals_fn,
            description="Lấy danh sách tất cả các bệnh viện."
        )
        self.search_hospitals = FunctionTool.from_defaults(
            fn=self.search_hospitals_fn,
            description="Tìm kiếm bệnh viện theo từ khóa. Truyền vào 'query'."
        )
        self.search_departments = FunctionTool.from_defaults(
            fn=self.search_departments_fn,
            description="Tìm kiếm các khoa trong bệnh viện. Truyền vào 'hospital_id'."
        )
        self.search_doctors = FunctionTool.from_defaults(
            fn=self.search_doctors_fn,
            description="Tìm kiếm bác sĩ theo bệnh viện và khoa. Truyền vào 'hospital_id' và 'department_id'."
        )
        self.get_available_appointments = FunctionTool.from_defaults(
            fn=self.get_available_appointments_fn,
            description="Lấy lịch hẹn có sẵn cho bác sĩ trong khoa tại bệnh viện. Truyền vào 'hospital_id', 'department_id', và 'doctor_id'."
        )
        self.create_appointment = FunctionTool.from_defaults(
            fn=self.create_appointment_fn,
            description="Đặt lịch hẹn mới. Truyền vào thông tin cần thiết."
        )

    def get_all_hospitals_fn(self, token: str) -> Union[str, dict]:
        try:
            # token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBleGFtcGxlLmNvbSIsImV4cCI6MTczNjE1NjAxOH0.9QWhRvkQSiey5DVpMwPdGUIGsHTLaLm_xVcH4o1djtc"
            # Hard code URL giống lệnh curl
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
        except requests.RequestException as e:
            print(f"Lỗi khi lấy danh sách bệnh viện: {str(e)}")
            return {"error": f"Lỗi khi lấy danh sách bệnh viện: {str(e)}"}

    def search_hospitals_fn(self, query: str) -> Union[List[dict], dict]:
        try:
            params = {'query': query}
            response = requests.get(f"{BASE_URL}/hospital/search", params=params)
            response.raise_for_status()
            hospitals = response.json()
            return hospitals  # Assuming the API returns a list of hospital dicts
        except requests.RequestException as e:
            return {"error": f"Lỗi khi tìm kiếm bệnh viện: {str(e)}"}

    def search_departments_fn(self, hospital_id: int) -> Union[List[dict], dict]:
        try:
            params = {'hospital_id': hospital_id}
            response = requests.get(f"{BASE_URL}/department/search", params=params)
            response.raise_for_status()
            departments = response.json()
            return departments  # Assuming the API returns a list of department dicts
        except requests.RequestException as e:
            return {"error": f"Lỗi khi tìm kiếm khoa: {str(e)}"}

    def search_doctors_fn(self, hospital_id: int, department_id: int) -> Union[List[dict], dict]:
        try:
            params = {
                'hospital_id': hospital_id,
                'department_id': department_id
            }
            response = requests.get(f"{BASE_URL}/doctor/search", params=params)
            response.raise_for_status()
            doctors = response.json()
            return doctors  # Assuming the API returns a list of doctor dicts
        except requests.RequestException as e:
            return {"error": f"Lỗi khi tìm kiếm bác sĩ: {str(e)}"}

    def get_available_appointments_fn(self, hospital_id: int, department_id: int, doctor_id: int) -> Union[List[dict], dict]:
        try:
            params = {
                'hospital_id': hospital_id,
                'department_id': department_id,
                'doctor_id': doctor_id
            }
            response = requests.get(f"{BASE_URL}/available-appointments", params=params)
            response.raise_for_status()
            appointments = response.json()
            return appointments  # Assuming the API returns a list of appointment dicts
        except requests.RequestException as e:
            return {"error": f"Lỗi khi lấy lịch hẹn có sẵn: {str(e)}"}

    def create_appointment_fn(self, appointment_data: dict) -> Union[str, dict]:
        """
        Expects appointment_data to be a dictionary with the following keys:
        - hospital_id (int)
        - department_id (int)
        - room_id (int)
        - doctor_id (int)
        - patient_id (int)
        - appointment_day (str, format YYYY-MM-DD)
        - appointment_shift (int)
        - reason (str)
        """
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(f"{BASE_URL}/appointments", json=appointment_data, headers=headers)
            response.raise_for_status()
            result = response.json()
            # Assuming the API returns a success message or the created appointment
            return result.get('message', f"Lịch hẹn đã được đặt thành công với ID {result.get('id', 'Unknown')}." )
        except requests.RequestException as e:
            return {"error": f"Lỗi khi đặt lịch hẹn: {str(e)}"}
