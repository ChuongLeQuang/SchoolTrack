class SchoolTrackError(Exception):
    """
    EN: Base exception for all SchoolTrack custom errors.
    VI: Ngoại lệ gốc cho toàn bộ ứng dụng SchoolTrack.
    """
    pass


class FileLockedError(SchoolTrackError):
    """
    EN: Raised when an Excel file is locked by another process (e.g., MS Excel).
    VI: Ngoại lệ tung ra khi file Excel bị khóa bởi một chương trình khác.
    """
    def __init__(self, file_path: str, message: str = None):
        self.file_path = file_path
        if not message:
            message = f"File đang bị mở hoặc khóa: {file_path}"
        super().__init__(message)