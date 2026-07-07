"""
사내 시스템 Mock 도구에 대한 간단한 유닛 테스트.
(실제 Claude API 호출 없이 실행 가능합니다.)

실행: pytest
"""
from src.tools.hr_system import apply_leave, get_attendance_summary, get_leave_balance


def test_get_leave_balance_known_employee():
    result = get_leave_balance("emp001")
    assert result["employee_id"] == "emp001"
    assert result["remaining_days"] == 12


def test_get_leave_balance_unknown_employee_uses_default():
    result = get_leave_balance("unknown_emp")
    assert result["remaining_days"] == 15


def test_apply_leave_returns_submitted_status():
    result = apply_leave("emp001", "2026-08-01", "2026-08-03")
    assert result["status"] == "submitted"
    assert result["start_date"] == "2026-08-01"


def test_attendance_summary_has_expected_keys():
    result = get_attendance_summary("emp001")
    assert "late_count" in result
    assert "remote_days" in result
