"""
EN: Script to run all unit tests in the project.
VI: Kịch bản để chạy toàn bộ unit test trong dự án.
"""
import sys
import pytest


def main() -> None:
    """
    EN: Main entry point for running tests.
    VI: Điểm neo chính để chạy kiểm thử.
    """
    print("🚀 Khởi động quá trình kiểm thử (Unit Tests) bằng Pytest...\n")
    
    # Chạy toàn bộ test trong thư mục tests với tuỳ chọn in chi tiết (-v)
    exit_code = pytest.main(["-v", "apps/main_app/tests/"])
    sys.exit(exit_code)


if __name__ == "__main__":
    main()