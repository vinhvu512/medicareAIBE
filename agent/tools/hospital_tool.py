import requests
class HospitalTool:import requests
from llama_index.core.tools import FunctionTool
from typing import List, Union
import os
from dotenv import load_dotenv

load_dotenv()


BASE_URL = os.getenv("BASE_URL")

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
                "Create a new appointment. Requires the following information in the request body:\n"
                "- 'hospital_id' (int): ID of the hospital.\n"
                "- 'department_id' (int): ID of the department.\n"
                "- 'doctor_id' (int): ID of the doctor.\n"
                "- 'patient_id' (int): ID of the patient.\n"
                "- 'appointment_day' (str): Appointment date in 'YYYY-MM-DD' format.\n"
                "- 'appointment_shift' (int): Shift number (0-19). Each day has 20 shifts of 30 minutes each:\n"
                "  * Shifts 0-9: Morning, starting at 7:30 AM (shift 0) and ending at 12:30 PM (shift 9).\n"
                "  * Shifts 10-19: Afternoon, starting at 1:30 PM (shift 10) and ending at 6:30 PM (shift 19).\n"
                "- 'reason' (str): Reason for the appointment.\n\n"
                "Example request body: It's raw dictionary, don't have AttributedDict\n"
                "{\n"
                "  'hospital_id': 1,\n"
                "  'department_id': 2,\n"
                "  'doctor_id': 15,\n"
                "  'patient_id': 7,\n"
                "  'appointment_day': '2025-01-23',\n"
                "  'appointment_shift': 8,\n"
                "  'reason': 'Routine check-up'\n"
                "}"
            )
)
        self.request_create = FunctionTool.from_defaults(
            fn=self.request_create,
            description=(
                """
                Nhắc lại thông tin người dùng đã cung cấp và yêu cầu xác nhận trước khi tạo lịch hẹn.
                    appointment_data (dict): Bao gồm các thông tin cần thiết để tạo lịch hẹn:
                    - hospital_id (int)
                    - department_id (int)
                    - doctor_id (int)
                    - patient_id (int)
                    - appointment_day (str, format YYYY-MM-DD)
                    - appointment_shift (int)
                    - reason (str)
                """
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
            hospital_list = "\n".join(
                [f"Hospital ID: {h['hospital_id']}, Tên: {h['hospital_name']}" for h in hospitals]
            )
            return hospital_list
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
            hospital_list = "\n".join(
                [f"Hospital ID: {h['hospital_id']}, Tên: {h['hospital_name']}" for h in hospitals]
            )
            return hospital_list
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
            department_list = "\n".join(
                [f"Department ID: {d['department_id']}, Tên: {d['department_name']}" for d in departments]
            )
            return department_list
        except requests.RequestException as e:
            print(f"Lỗi khi tìm kiếm khoa: {str(e)}")
            return {"error": f"Lỗi khi tìm kiếm khoa: {str(e)}"}
    def search_doctors_fn(self, hospital_id: int, department_id: int) -> Union[List[str], dict]:
        """
        Tìm kiếm bác sĩ theo bệnh viện và khoa. Trả về danh sách các bác sĩ dưới dạng chuỗi
        định dạng 'Doctor ID: {user_id}, Tên: {fullname}'.
        """
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

            # Format output as requested
            formatted_doctors = [
                f"Doctor ID: {doctor['user_id']}, Tên: {doctor['fullname']}" 
                for doctor in doctors
            ]
            return formatted_doctors
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
    def request_create(self, appointment_data: dict) -> str:
        # Extract and format details for confirmation
        hospital_id = appointment_data.get("hospital_id")
        department_id = appointment_data.get("department_id")
        doctor_id = appointment_data.get("doctor_id")
        patient_id = appointment_data.get("patient_id")
        appointment_day = appointment_data.get("appointment_day")
        appointment_shift = appointment_data.get("appointment_shift")
        reason = appointment_data.get("reason")

        shift_time = (
            f"{7 + (appointment_shift // 2)}:{'30' if appointment_shift % 2 else '00'} AM"
            if appointment_shift < 10
            else f"{1 + ((appointment_shift - 10) // 2)}:{'30' if appointment_shift % 2 else '00'} PM"
        )

        confirmation_message = (
            f"Thông tin lịch hẹn của bạn:\n"
            f"- Bệnh viện ID: {hospital_id}\n"
            f"- Khoa ID: {department_id}\n"
            f"- Bác sĩ ID: {doctor_id}\n"
            f"- Bệnh nhân ID: {patient_id}\n"
            f"- Ngày hẹn: {appointment_day}\n"
            f"- Ca hẹn: {appointment_shift} (thời gian: {shift_time})\n"
            f"- Lý do: {reason}\n"
            "Bạn có muốn xác nhận tạo lịch hẹn này không? (yes/no)"
        )

        print(confirmation_message)

        # Assuming we get user input directly here
        user_confirmation = input("Nhập 'yes' để xác nhận, hoặc 'no' để hủy: ").strip().lower()

        if user_confirmation == 'yes':
            # Proceed to create appointment
            return self.create_appointment_fn(appointment_data)
        else:
            return "Lịch hẹn đã bị hủy bởi người dùng."

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
            # Extract data from AttributedDict wrapper if present
            if isinstance(appointment_data, dict) and 'appointment_data' in appointment_data:
                appointment_data = dict(appointment_data['appointment_data'])

            # Validate required fields
            required_fields = ['hospital_id', 'department_id', 'doctor_id', 
                            'patient_id', 'appointment_day', 'appointment_shift', 'reason']
            
            for field in required_fields:
                if appointment_data.get(field) is None:
                    return {"error": f"Thiếu thông tin bắt buộc: {field}"}

            # Add status field
            appointment_data['status'] = 'Scheduled'

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
            return result.get('message', f"Lịch hẹn đã được tạo thành công.")
        except requests.RequestException as e:
            print(f"Lỗi khi tạo lịch hẹn: {str(e)}")
            return {"error": f"Lỗi khi tạo lịch hẹn: {str(e)}"}