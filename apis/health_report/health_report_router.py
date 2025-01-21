from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List
from models.health_report import HealthReport
from schemas.health_report import HealthReportCreate, HealthReportResponse, PredictionResult
from database.session import get_db
from models.appointment import Appointment
from models.user import User
from apis.authenticate.authenticate import get_current_patient  # Giả sử bạn đã có hệ thống xác thực
# from services.prediction_service import predict_diseases  # Bạn cần triển khai dịch vụ này

import json

router = APIRouter()

@router.post("")
async def create_health_report(
    report: HealthReportCreate,
    db: Session = Depends(get_db)
    # current_user: User = Depends(get_current_patient)
):
    """
    Tạo báo cáo sức khỏe từ nội dung cuộc trò chuyện và lưu vào database.
    """
    # Kiểm tra liệu cuộc hẹn có tồn tại và thuộc về người dùng hiện tại
    print(report.appointment_id)
    appointment = db.query(Appointment).filter(
        Appointment.appointment_id == report.appointment_id,
        # Appointment.patient_id == current_user.user_id
    ).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Cuộc hẹn không tìm thấy")

    existing_report = db.query(HealthReport).filter(
        HealthReport.appointment_id == report.appointment_id
    ).first()

    if existing_report:
        return existing_report

    sample_prediction_result = {
        "ThongTinBenhNhan": {
            "HoVaTen": "Vũ Xuân Vinh",
            "Tuoi": "20",
            "GioiTinh": "Nam",
            "LienHe": "0778984805"
        },
        "TrieuChungVaPhanNan": {
            "MoTa": "Bệnh nhân báo cáo ngứa và đỏ da tại vùng cổ tay, lan đến cánh tay.",
            "ThoiGianBatDau": "Vài ngày trước sau khi sử dụng một chiếc vòng tay mới.",
            "TrieuChungChiTiet": [
                "Ngứa",
                "Đỏ da", 
                "Khô",
                "Tróc vảy",
                "Một số mụn nước nhỏ"
            ]
        },
        "KetQuaSoBo": {
            "ChanDoanAI": "Viêm da tiếp xúc dị ứng",
            "NguyenNhanDuKien": "Do tiếp xúc với kim loại trong chiếc vòng tay."
        },
        "KhuyenNghiChoBacSi": [
            "Yêu cầu bệnh nhân ngừng sử dụng vòng tay nghi ngờ là nguyên nhân.",
            "Tửng thực kiểm tra lâm sàng vùng da bị tác động.",
            "Xem xét kê đơn kem bôi corticosteroid nhẹ và thuốc kháng histamine nếu ngứa nhiều.",
            "Khuyên bệnh nhân dợ rửa vùng da tác động với nước sạch và xà phòng không gây kích ứng."
        ],
        "LuuYGuiBacSi": "Báo cáo này được tạo tự động bởi hệ thống AI nhằm cung cấp tóm tắt ban đầu cho bác sĩ tham khảo. Vui lòng xác nhận kết quả qua khám lâm sàng và xét nghiệm."
    }

    json_result = json.dumps(sample_prediction_result, ensure_ascii=False, indent=4)

    # Tạo bản ghi HealthReport
    health_report = HealthReport(
        appointment_id=report.appointment_id,
        patient_id=appointment.patient_id,
        chat_content=report.chat_content,
        prediction_results=json_result  # Giả sử prediction là dict hoặc list
    )

    print(json_result)

    db.add(health_report)
    db.commit()
    db.refresh(health_report)

    return health_report


# @router.get("/{report_id}", response_model=HealthReportResponse)
# async def get_health_report(
#     report_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_patient)
# ):
#     """
#     Lấy thông tin chi tiết của một báo cáo sức khỏe.
#     """
#     health_report = db.query(HealthReport).join(Appointment).filter(
#         HealthReport.report_id == report_id,
#         Appointment.patient_id == current_user.patient.patient_id
#     ).first()

#     if not health_report:
#         raise HTTPException(status_code=404, detail="Báo cáo không tìm thấy")

#     return health_report


@router.get("", response_model=List[HealthReportResponse])
async def list_health_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient)
):
    """
    Lấy danh sách tất cả các báo cáo sức khỏe của người dùng hiện tại.
    """
    reports = db.query(HealthReport).join(Appointment).filter(
        Appointment.patient_id == current_user.patient.patient_id
    ).all()

    return reports


@router.get("/latest", response_model=HealthReportResponse)
async def get_latest_health_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_patient)
):
    """
    Lấy báo cáo sức khỏe mới nhất của người dùng hiện tại.
    """
    try:
        # Truy vấn báo cáo mới nhất dựa trên thời gian tạo
        latest_report = db.query(HealthReport)\
            .join(Appointment)\
            .filter(Appointment.patient_id == current_user.patient.patient_id)\
            .order_by(HealthReport.created_at.desc())\
            .first()
        
        if not latest_report:
            raise HTTPException(status_code=404, detail="Không tìm thấy báo cáo sức khỏe nào.")
        
        return latest_report
    
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"Lỗi khi lấy báo cáo sức khỏe mới nhất: {str(e)}",
                "code": 500
            }
        )
    
@router.get("/appointment/{appointment_id}/", response_model=HealthReportResponse)
async def get_reports_by_appointment(
    appointment_id: int = Path(..., description="ID của cuộc hẹn cần lấy báo cáo"),
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_patient)
):
    """
    Lấy báo cáo sức khỏe mới nhất của một cuộc hẹn cụ thể.
    """
    try:
        appointment = db.query(Appointment).filter(
            Appointment.appointment_id == appointment_id,
            # Appointment.patient_id == current_user.user_id
        ).first()
        
        if not appointment:
            raise HTTPException(status_code=404, detail="Cuộc hẹn không tìm thấy hoặc không thuộc về bạn.")
        
        # Get only the latest report
        latest_report = db.query(HealthReport).filter(
            HealthReport.appointment_id == appointment_id
        ).order_by(HealthReport.created_at.desc()).first()
        
        if not latest_report:
            raise HTTPException(status_code=404, detail="Không tìm thấy báo cáo sức khỏe nào cho cuộc hẹn này.")
        
        return latest_report
    
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"Lỗi khi lấy báo cáo sức khỏe: {str(e)}",
                "code": 500
            }
        )

