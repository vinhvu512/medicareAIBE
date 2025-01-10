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


BASE_URL = "http://127.0.0.1:8000/api"

class HospitalTool:
    def __init__(self):
        """
        Khởi tạo lớp HospitalTool.
        Cung cấp các công cụ để thực hiện các tác vụ liên quan đến quản lý bệnh viện, bao gồm:
        - Lấy danh sách tất cả các bệnh viện.
        - Tìm kiếm bệnh viện theo từ khóa.
        - Tìm kiếm khoa theo bệnh viện.
        - Tìm kiếm bác sĩ trong khoa của một bệnh viện cụ thể.
        - Lấy danh sách lịch hẹn có sẵn cho một bác sĩ.
        - Tạo lịch hẹn mới.

        Các phương thức được triển khai thông qua `FunctionTool` để dễ dàng tích hợp vào hệ thống.
        """
        self._token_provider = None  # Bộ cung cấp token xác thực.

        # Lấy danh sách tất cả các bệnh viện.
        self.get_all_hospitals = FunctionTool.from_defaults(
            fn=self.get_all_hospitals_fn,
            description="Lấy danh sách tất cả các bệnh viện hiện có. Không yêu cầu tham số. "
        )

        # Tìm kiếm bệnh viện theo từ khóa.
        self.search_hospitals = FunctionTool.from_defaults(
            fn=self.search_hospitals_fn,
            description="Tìm kiếm bệnh viện theo từ khóa. Tham số: 'query' (chuỗi từ khóa để tìm kiếm)."
        )

        # Tìm kiếm các khoa trong một bệnh viện.
        self.search_departments = FunctionTool.from_defaults(
            fn=self.search_departments_fn,
            description="Tìm kiếm các khoa trong bệnh viện. Tham số: 'hospital_id' (ID của bệnh viện)."
        )

        # Tìm kiếm bác sĩ theo bệnh viện và khoa.
        self.search_doctors = FunctionTool.from_defaults(
            fn=self.search_doctors_fn,
            description="Tìm kiếm bác sĩ theo bệnh viện và khoa. Tham số: 'hospital_id' và 'department_id'."
        )

        # Lấy lịch hẹn có sẵn.
        self.get_available_appointments = FunctionTool.from_defaults(
            fn=self.get_available_appointments_fn,
            description="Lấy lịch hẹn có sẵn cho bác sĩ trong khoa tại bệnh viện. "
                        "Tham số: 'hospital_id', 'department_id', và 'doctor_id'."
        )

        # Đặt lịch hẹn mới.
        self.create_appointment = FunctionTool.from_defaults(
            fn=self.create_appointment_fn,
            description=(
                "Đặt lịch hẹn mới. Yêu cầu cung cấp các thông tin sau trong body request: "
                "- 'hospital_id' (int): ID bệnh viện. "
                "- 'department_id' (int): ID khoa. "
                "- 'room_id' (int): ID phòng khám. "
                "- 'doctor_id' (int): ID bác sĩ. "
                "- 'patient_id' (int): ID bệnh nhân. "
                "- 'appointment_day' (str): Ngày hẹn (định dạng YYYY-MM-DD). "
                "- 'appointment_shift' (int): Ca hẹn. Mỗi ngày sẽ có 20 ca hẹn được đánh số từ 0 đến 19, khoảng thời gian khám mỗi ca là 30 phút. Ca từ 0 đến 9 là ca buổi sáng bắt đầu từ lúc 7h30 (ca 0) và kết thúc lúc 12h30 (ca 9). Ca từ 10 đến 19 là ca buổi chiều bắt đầu từ lúc 13h30 (ca 10) và kết thúc lúc 18h30 (ca 19). Bạn hãy từ các số int mà tự quy ra khung giờ trong ngày và ngược lại."
                "- 'reason' (str): Lý do hẹn."
            )
        )

    def set_token_provider(self, provider):
        """Set the function that will provide the token"""
        self._token_provider = provider

    def get_token(self):
        """Get the current token from the provider"""
        if self._token_provider:
            return self._token_provider()
        return None

    def get_all_hospitals_fn(self) -> Union[str, dict]:
        try:
            token = self.get_token()
            url = f"{BASE_URL}/hospitals"
            headers = {'Authorization': f'Bearer {token}'}

            print(f"Gửi yêu cầu GET đến {url}")
            response = requests.get(url, headers=headers, timeout=3000)

            print("Mã trạng thái:", response.status_code)
            print("Nội dung phản hồi:", response.text)
            response.raise_for_status()

            hospitals = response.json()
            # hospital_list = "\n".join(
            #     [f"ID: {h['hospital_id']}, Tên: {h['hospital_name']}, Địa chỉ: {h['hospital_address']}" for h in hospitals]
            # )
            return hospitals
        except requests.RequestException as e:
            print(f"Lỗi khi lấy danh sách bệnh viện: {str(e)}")
            return {"error": f"Lỗi khi lấy danh sách bệnh viện: {str(e)}"}

    def search_hospitals_fn(self, query: str) -> Union[List[dict], dict]:
        try:
            token = self.get_token()
            url = f"{BASE_URL}/hospitals/search"
            headers = {'Authorization': f'Bearer {token}'}
            params = {'query': query}

            print(f"Gửi yêu cầu GET đến {url}")
            response = requests.get(url, headers=headers, params=params, timeout=3000)

            print("Mã trạng thái:", response.status_code)
            print("Nội dung phản hồi:", response.text)
            response.raise_for_status()

            hospitals = response.json()
            return hospitals
        except requests.RequestException as e:
            print(f"Lỗi khi tìm kiếm bệnh viện: {str(e)}")
            return {"error": f"Lỗi khi tìm kiếm bệnh viện: {str(e)}"}

    def search_departments_fn(self, hospital_id: int) -> Union[List[dict], dict]:
        try:
            token = self.get_token()
            url = f"{BASE_URL}/departments/search"
            headers = {'Authorization': f'Bearer {token}'}
            params = {'hospital_id': hospital_id}

            print(f"Gửi yêu cầu GET đến {url}")
            response = requests.get(url, headers=headers, params=params, timeout=3000)

            print("Mã trạng thái:", response.status_code)
            print("Nội dung phản hồi:", response.text)
            response.raise_for_status()

            departments = response.json()
            return departments
        except requests.RequestException as e:
            print(f"Lỗi khi tìm kiếm khoa: {str(e)}")
            return {"error": f"Lỗi khi tìm kiếm khoa: {str(e)}"}

    def search_doctors_fn(self, hospital_id: int, department_id: int) -> Union[List[dict], dict]:
        try:
            token = self.get_token()
            url = f"{BASE_URL}/doctors/search"
            headers = {'Authorization': f'Bearer {token}'}
            params = {
                'hospital_id': hospital_id,
                'department_id': department_id
            }

            print(f"Gửi yêu cầu GET đến {url}")
            response = requests.get(url, headers=headers, params=params, timeout=3000)

            print("Mã trạng thái:", response.status_code)
            print("Nội dung phản hồi:", response.text)
            response.raise_for_status()

            doctors = response.json()
            return doctors
        except requests.RequestException as e:
            print(f"Lỗi khi tìm kiếm bác sĩ: {str(e)}")
            return {"error": f"Lỗi khi tìm kiếm bác sĩ: {str(e)}"}

    def get_available_appointments_fn(self, hospital_id: int, department_id: int, doctor_id: int) -> Union[List[dict], dict]:
        try:
            token = self.get_token()
            url = f"{BASE_URL}/appointments/available-appointments"
            headers = {'Authorization': f'Bearer {token}'}
            params = {
                'hospital_id': hospital_id,
                'department_id': department_id,
                'doctor_id': doctor_id
            }

            print(f"Gửi yêu cầu GET đến {url}")
            response = requests.get(url, headers=headers, params=params, timeout=3000)

            print("Mã trạng thái:", response.status_code)
            print("Nội dung phản hồi:", response.text)
            response.raise_for_status()

            appointments = response.json()
            return appointments
        except requests.RequestException as e:
            print(f"Lỗi khi lấy lịch hẹn có sẵn: {str(e)}")
            return {"error": f"Lỗi khi lấy lịch hẹn có sẵn: {str(e)}"}
    def create_appointment_fn(self, appointment_data: dict) -> Union[str, dict]:
        """
        Tạo lịch hẹn mới. 
        Dữ liệu đầu vào:
        - hospital_id (int)
        - department_id (int)
        - doctor_id (int)
        - patient_id (int)
        - appointment_day (str, format YYYY-MM-DD)
        - appointment_shift (int)
        - reason (str)
        """
        try:
            token = self.get_token()
            url = f"{BASE_URL}/appointments"
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }

            print(f"Gửi yêu cầu POST đến {url} với dữ liệu: {appointment_data}")
            response = requests.post(url, headers=headers, json=appointment_data, timeout=3000)

            print("Mã trạng thái:", response.status_code)
            print("Nội dung phản hồi:", response.text)
            response.raise_for_status()

            result = response.json()
            # Assuming API trả về message thành công hoặc ID của lịch hẹn
            return result.get('message', f"Lịch hẹn đã được tạo thành công với ID {result.get('id', 'Unknown')}.")
        except requests.RequestException as e:
            print(f"Lỗi khi tạo lịch hẹn: {str(e)}")
            return {"error": f"Lỗi khi tạo lịch hẹn: {str(e)}"}
