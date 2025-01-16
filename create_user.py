import requests
import json
from datetime import date, datetime

def test_signup_users():
    url = "http://localhost:8000/api/doctor/schedule/"
    
    # Danh sách bác sĩ
    
    doctors_data = [
    # 5 bác sĩ Tim mạch
        {
            "username": "bscardiac1",
            "email": "bscardiac1@gmail.com",
            "password": "1234",
            "fullname": "Nguyễn Văn Thành",
            "date_of_birth": "1980-01-15",
            "gender": "Male",
            "user_type": "Doctor",
            "address": "123 Lê Lợi, Quận 1, TP.HCM",
            "phone": "0901234567",
            "profile_image": "https://example.com/bscardiac1.jpg",
            "doctor_specialty": "Tim mạch",
            "doctor_experience": 15
        },
        {
            "username": "bscardiac2",
            "email": "bscardiac2@gmail.com",
            "password": "1234",
            "fullname": "Trần Thị An",
            "date_of_birth": "1985-03-20",
            "gender": "Female",
            "user_type": "Doctor",
            "address": "234 Nguyễn Huệ, Quận 3, TP.HCM",
            "phone": "0912345678",
            "profile_image": "https://example.com/bscardiac2.jpg",
            "doctor_specialty": "Tim mạch",
            "doctor_experience": 12
        },
        {
            "username": "bscardiac3",
            "email": "bscardiac3@gmail.com",
            "password": "1234",
            "fullname": "Phạm Hoàng Nam",
            "date_of_birth": "1975-05-10",
            "gender": "Male",
            "user_type": "Doctor",
            "address": "56 Hùng Vương, Quận 5, TP.HCM",
            "phone": "0923456789",
            "profile_image": "https://example.com/bscardiac3.jpg",
            "doctor_specialty": "Tim mạch",
            "doctor_experience": 20
        },
        {
            "username": "bscardiac4",
            "email": "bscardiac4@gmail.com",
            "password": "1234",
            "fullname": "Hoàng Thị Tuyết",
            "date_of_birth": "1982-08-25",
            "gender": "Female",
            "user_type": "Doctor",
            "address": "78 Trường Chinh, Quận Tân Bình, TP.HCM",
            "phone": "0934567890",
            "profile_image": "https://example.com/bscardiac4.jpg",
            "doctor_specialty": "Tim mạch",
            "doctor_experience": 18
        },
        {
            "username": "bscardiac5",
            "email": "bscardiac5@gmail.com",
            "password": "1234",
            "fullname": "Nguyễn Quốc Anh",
            "date_of_birth": "1990-07-01",
            "gender": "Male",
            "user_type": "Doctor",
            "address": "12 Lý Tự Trọng, Quận 1, TP.HCM",
            "phone": "0945678901",
            "profile_image": "https://example.com/bscardiac5.jpg",
            "doctor_specialty": "Tim mạch",
            "doctor_experience": 10
        },

        # 5 bác sĩ Sản phụ khoa
        {
            "username": "bsobst1",
            "email": "bsobst1@gmail.com",
            "password": "1234",
            "fullname": "Nguyễn Thị Lan",
            "date_of_birth": "1985-04-12",
            "gender": "Female",
            "user_type": "Doctor",
            "address": "345 Điện Biên Phủ, Quận 3, TP.HCM",
            "phone": "0901122334",
            "profile_image": "https://example.com/bsobst1.jpg",
            "doctor_specialty": "Sản phụ khoa",
            "doctor_experience": 12
        },
        {
            "username": "bsobst2",
            "email": "bsobst2@gmail.com",
            "password": "1234",
            "fullname": "Trần Thanh Hà",
            "date_of_birth": "1990-03-10",
            "gender": "Female",
            "user_type": "Doctor",
            "address": "567 Võ Văn Kiệt, Quận 5, TP.HCM",
            "phone": "0912333445",
            "profile_image": "https://example.com/bsobst2.jpg",
            "doctor_specialty": "Sản phụ khoa",
            "doctor_experience": 8
        },
        {
            "username": "bsobst3",
            "email": "bsobst3@gmail.com",
            "password": "1234",
            "fullname": "Hoàng Mai Anh",
            "date_of_birth": "1987-01-20",
            "gender": "Female",
            "user_type": "Doctor",
            "address": "789 Nguyễn Thị Minh Khai, Quận 1, TP.HCM",
            "phone": "0921223344",
            "profile_image": "https://example.com/bsobst3.jpg",
            "doctor_specialty": "Sản phụ khoa",
            "doctor_experience": 10
        },
        {
            "username": "bsobst4",
            "email": "bsobst4@gmail.com",
            "password": "1234",
            "fullname": "Lê Phương Nam",
            "date_of_birth": "1983-06-30",
            "gender": "Male",
            "user_type": "Doctor",
            "address": "123 Trần Quý Cáp, Quận 3, TP.HCM",
            "phone": "0933445566",
            "profile_image": "https://example.com/bsobst4.jpg",
            "doctor_specialty": "Sản phụ khoa",
            "doctor_experience": 15
        },
        {
            "username": "bsobst5",
            "email": "bsobst5@gmail.com",
            "password": "1234",
            "fullname": "Phạm Thu Hương",
            "date_of_birth": "1989-09-15",
            "gender": "Female",
            "user_type": "Doctor",
            "address": "345 Nguyễn Văn Linh, Quận 7, TP.HCM",
            "phone": "0944556677",
            "profile_image": "https://example.com/bsobst5.jpg",
            "doctor_specialty": "Sản phụ khoa",
            "doctor_experience": 10
        },

        # 5 bác sĩ Nhi khoa
        {
            "username": "bspedia1",
            "email": "bspedia1@gmail.com",
            "password": "1234",
            "fullname": "Nguyễn Hoàng Long",
            "date_of_birth": "1980-02-28",
            "gender": "Male",
            "user_type": "Doctor",
            "address": "456 Nguyễn Thái Bình, Quận 1, TP.HCM",
            "phone": "0911223344",
            "profile_image": "https://example.com/bspedia1.jpg",
            "doctor_specialty": "Nhi khoa",
            "doctor_experience": 20
        },
        {
            "username": "bspedia2",
            "email": "bspedia2@gmail.com",
            "password": "1234",
            "fullname": "Phạm Thanh Huyền",
            "date_of_birth": "1992-05-15",
            "gender": "Female",
            "user_type": "Doctor",
            "address": "789 Lê Hồng Phong, Quận 10, TP.HCM",
            "phone": "0935667788",
            "profile_image": "https://example.com/bspedia2.jpg",
            "doctor_specialty": "Nhi khoa",
            "doctor_experience": 12
        },
        {
            "username": "bspedia3",
            "email": "bspedia3@gmail.com",
            "password": "1234",
            "fullname": "Hoàng Quang Minh",
            "date_of_birth": "1985-07-25",
            "gender": "Male",
            "user_type": "Doctor",
            "address": "456 Tôn Đức Thắng, Quận Bình Thạnh, TP.HCM",
            "phone": "0944332211",
            "profile_image": "https://example.com/bspedia3.jpg",
            "doctor_specialty": "Nhi khoa",
            "doctor_experience": 15
        },
        {
            "username": "bspedia4",
            "email": "bspedia4@gmail.com",
            "password": "1234",
            "fullname": "Lê Minh Châu",
            "date_of_birth": "1988-03-12",
            "gender": "Female",
            "user_type": "Doctor",
            "address": "678 Võ Thị Sáu, Quận 3, TP.HCM",
            "phone": "0955334455",
            "profile_image": "https://example.com/bspedia4.jpg",
            "doctor_specialty": "Nhi khoa",
            "doctor_experience": 10
        },
        {
            "username": "bspedia5",
            "email": "bspedia5@gmail.com",
            "password": "1234",
            "fullname": "Nguyễn Văn Tú",
            "date_of_birth": "1983-11-22",
            "gender": "Male",
            "user_type": "Doctor",
            "address": "789 Đinh Tiên Hoàng, Quận Bình Thạnh, TP.HCM",
            "phone": "0965443322",
            "profile_image": "https://example.com/bspedia5.jpg",
            "doctor_specialty": "Nhi khoa",
            "doctor_experience": 17
        },

        # 5 bác sĩ Đa khoa
        {
            "username": "bsgeneral1",
            "email": "bsgeneral1@gmail.com",
            "password": "1234",
            "fullname": "Lê Văn Bình",
            "date_of_birth": "1970-01-01",
            "gender": "Male",
            "user_type": "Doctor",
            "address": "123 Nguyễn Trãi, Quận 1, TP.HCM",
            "phone": "0935667788",
            "profile_image": "https://example.com/bsgeneral1.jpg",
            "doctor_specialty": "Đa khoa",
            "doctor_experience": 25
        },
        {
            "username": "bsgeneral2",
            "email": "bsgeneral2@gmail.com",
            "password": "1234",
            "fullname": "Hoàng Thị Hồng",
            "date_of_birth": "1982-04-15",
            "gender": "Female",
            "user_type": "Doctor",
            "address": "234 Lý Tự Trọng, Quận 1, TP.HCM",
            "phone": "0944223344",
            "profile_image": "https://example.com/bsgeneral2.jpg",
            "doctor_specialty": "Đa khoa",
            "doctor_experience": 18
        },
        {
            "username": "bsgeneral3",
            "email": "bsgeneral3@gmail.com",
            "password": "1234",
            "fullname": "Trần Quốc Bảo",
            "date_of_birth": "1989-06-22",
            "gender": "Male",
            "user_type": "Doctor",
            "address": "345 Nguyễn Văn Linh, Quận 7, TP.HCM",
            "phone": "0954332211",
            "profile_image": "https://example.com/bsgeneral3.jpg",
            "doctor_specialty": "Đa khoa",
            "doctor_experience": 12
        },
        {
            "username": "bsgeneral4",
            "email": "bsgeneral4@gmail.com",
            "password": "1234",
            "fullname": "Nguyễn Quỳnh Mai",
            "date_of_birth": "1990-08-20",
            "gender": "Female",
            "user_type": "Doctor",
            "address": "456 Võ Văn Tần, Quận 3, TP.HCM",
            "phone": "0912334556",
            "profile_image": "https://example.com/bsgeneral4.jpg",
            "doctor_specialty": "Đa khoa",
            "doctor_experience": 10
        },
        {
            "username": "bsgeneral5",
            "email": "bsgeneral5@gmail.com",
            "password": "1234",
            "fullname": "Lê Minh Sơn",
            "date_of_birth": "1987-09-12",
            "gender": "Male",
            "user_type": "Doctor",
            "address": "789 Tôn Đức Thắng, Quận 1, TP.HCM",
            "phone": "0944556677",
            "profile_image": "https://example.com/bsgeneral5.jpg",
            "doctor_specialty": "Đa khoa",
            "doctor_experience": 13
        }
    ]

    patients_data = [
        # {
        #     "username": "nguyenvannam",
        #     "email": "nguyenvannam@gmail.com",
        #     "password": "1234",
        #     "fullname": "Nguyễn Văn Nam",
        #     "date_of_birth": "1990-01-15",
        #     "gender": "Male",
        #     "user_type": "Patient",
        #     "address": "234 Lê Lai, Quận 1, TP.HCM",
        #     "phone": "0934567890",
        #     "profile_image": "https://example.com/patient1.jpg"
        # },
        # {
        #     "username": "tranthiha",
        #     "email": "tranthiha@gmail.com",
        #     "password": "1234",
        #     "fullname": "Trần Thị Hà",
        #     "date_of_birth": "1995-06-20",
        #     "gender": "Female",
        #     "user_type": "Patient",
        #     "address": "56 Nguyễn Du, Quận 1, TP.HCM",
        #     "phone": "0945678901",
        #     "profile_image": "https://example.com/patient2.jpg"
        # },
        # {
        #     "username": "levanbinh",
        #     "email": "levanbinh@gmail.com",
        #     "password": "1234",
        #     "fullname": "Lê Văn Bình",
        #     "date_of_birth": "1988-12-25",
        #     "gender": "Male",
        #     "user_type": "Patient",
        #     "address": "789 Cách Mạng Tháng 8, Quận 3, TP.HCM",
        #     "phone": "0956789012",
        #     "profile_image": "https://example.com/patient3.jpg"
        # },
        # {
        #     "username": "hoangthanh",
        #     "email": "hoangthanh@gmail.com",
        #     "password": "1234",
        #     "fullname": "Hoàng Thanh",
        #     "date_of_birth": "2000-08-14",
        #     "gender": "Male",
        #     "user_type": "Patient",
        #     "address": "123 Nguyễn Văn Trỗi, Quận Phú Nhuận, TP.HCM",
        #     "phone": "0978123456",
        #     "profile_image": "https://example.com/patient4.jpg"
        # },
        # {
        #     "username": "ngocthuy",
        #     "email": "ngocthuy@gmail.com",
        #     "password": "1234",
        #     "fullname": "Nguyễn Ngọc Thúy",
        #     "date_of_birth": "1997-04-22",
        #     "gender": "Female",
        #     "user_type": "Patient",
        #     "address": "567 Lê Lợi, Quận 1, TP.HCM",
        #     "phone": "0912345678",
        #     "profile_image": "https://example.com/patient5.jpg"
        # },
        # {
        #     "username": "phamvudong",
        #     "email": "phamvudong@gmail.com",
        #     "password": "1234",
        #     "fullname": "Phạm Vũ Đông",
        #     "date_of_birth": "1985-11-30",
        #     "gender": "Male",
        #     "user_type": "Patient",
        #     "address": "78 Hoàng Văn Thụ, Quận Tân Bình, TP.HCM",
        #     "phone": "0923456789",
        #     "profile_image": "https://example.com/patient6.jpg"
        # },
        # {
        #     "username": "tranphuong",
        #     "email": "tranphuong@gmail.com",
        #     "password": "1234",
        #     "fullname": "Trần Phương",
        #     "date_of_birth": "1992-03-10",
        #     "gender": "Female",
        #     "user_type": "Patient",
        #     "address": "34 Điện Biên Phủ, Quận Bình Thạnh, TP.HCM",
        #     "phone": "0943216547",
        #     "profile_image": "https://example.com/patient7.jpg"
        # },
        # {
        #     "username": "danghuy",
        #     "email": "danghuy@gmail.com",
        #     "password": "1234",
        #     "fullname": "Đặng Huy",
        #     "date_of_birth": "1998-09-07",
        #     "gender": "Male",
        #     "user_type": "Patient",
        #     "address": "45 Trần Hưng Đạo, Quận 1, TP.HCM",
        #     "phone": "0937654321",
        #     "profile_image": "https://example.com/patient8.jpg"
        # },
        # {
        #     "username": "phamhoa",
        #     "email": "phamhoa@gmail.com",
        #     "password": "1234",
        #     "fullname": "Phạm Hoa",
        #     "date_of_birth": "1994-12-01",
        #     "gender": "Female",
        #     "user_type": "Patient",
        #     "address": "123 Lý Tự Trọng, Quận 1, TP.HCM",
        #     "phone": "0965432109",
        #     "profile_image": "https://example.com/patient9.jpg"
        # },
        # {
        #     "username": "tranviet",
        #     "email": "tranviet@gmail.com",
        #     "password": "1234",
        #     "fullname": "Trần Việt",
        #     "date_of_birth": "1989-06-06",
        #     "gender": "Male",
        #     "user_type": "Patient",
        #     "address": "789 Võ Thị Sáu, Quận 3, TP.HCM",
        #     "phone": "0912121212",
        #     "profile_image": "https://example.com/patient10.jpg"
        # }
    ]

    headers = {
        'Content-Type': 'application/json'
    }

    # Đăng ký bác sĩ
    print("Đăng ký tài khoản bác sĩ:")
    for doctor in doctors_data:
        try:
            response = requests.post(url, json=doctor, headers=headers)
            print(f"\nĐăng ký bác sĩ {doctor['fullname']}:")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Lỗi khi đăng ký bác sĩ {doctor['fullname']}: {str(e)}")

    # Đăng ký bệnh nhân 
    print("\nĐăng ký tài khoản bệnh nhân:")
    for patient in patients_data:
        try:
            response = requests.post(url, json=patient, headers=headers)
            print(f"\nĐăng ký bệnh nhân {patient['fullname']}:")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Lỗi khi đăng ký bệnh nhân {patient['fullname']}: {str(e)}")

if __name__ == "__main__":
    test_signup_users()