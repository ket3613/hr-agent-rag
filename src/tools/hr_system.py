"""
사내 인사 시스템(휴가/근태) 연동을 흉내 낸 Mock 모듈입니다.

⚠️ 실제 사내 API 엔드포인트, 인증 정보(SSO 등)는 포함되어 있지 않습니다.
운영 환경에 연동할 때는 이 파일의 각 함수 내부 구현만 실제 API 호출로
교체하면 되며, 함수 시그니처(입력/출력)는 그대로 유지하는 것을 권장합니다.
"""
from datetime import date

# 데모용 가짜 휴가 잔여일수 데이터
_MOCK_LEAVE_BALANCE: dict[str, int] = {
    "emp001": 12,
    "emp002": 7,
}


def get_leave_balance(employee_id: str) -> dict:
    """직원의 잔여 연차 일수를 조회합니다. (Mock)"""
    balance = _MOCK_LEAVE_BALANCE.get(employee_id, 15)
    return {
        "employee_id": employee_id,
        "remaining_days": balance,
        "as_of": str(date.today()),
    }


def apply_leave(employee_id: str, start_date: str, end_date: str) -> dict:
    """휴가 신청을 접수합니다. (Mock — 실제 승인 처리는 연동 필요)"""
    return {
        "employee_id": employee_id,
        "status": "submitted",
        "start_date": start_date,
        "end_date": end_date,
        "message": "휴가 신청이 접수되었습니다. (데모 응답이며 실제로 처리되지 않습니다)",
    }


def get_attendance_summary(employee_id: str) -> dict:
    """이번 달 근태 요약 정보를 조회합니다. (Mock)"""
    return {
        "employee_id": employee_id,
        "month": date.today().strftime("%Y-%m"),
        "late_count": 0,
        "remote_days": 3,
    }


# 도구 이름 -> 실제 함수 매핑 (에이전트가 이 레지스트리를 통해 도구를 호출)
TOOL_REGISTRY = {
    "get_leave_balance": get_leave_balance,
    "apply_leave": apply_leave,
    "get_attendance_summary": get_attendance_summary,
}
