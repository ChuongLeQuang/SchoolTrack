import unicodedata
import re


class TextUtils:
    """
    EN: Utility class for text manipulation and normalization.
    VI: Lớp tiện ích để xử lý và chuẩn hóa chuỗi văn bản.
    """

    @staticmethod
    def normalize_vietnamese(text: str) -> str:
        """
        EN: Remove Vietnamese accents, convert to lowercase, and remove extra spaces.
        VI: Chuyển chuỗi tiếng Việt thành chữ thường, không dấu và xóa khoảng trắng thừa.
        """
        if not text:
            return ""
            
        # 1. Chuyển thành chữ thường và xóa khoảng trắng 2 đầu
        text = str(text).lower().strip()
        # 2. Xử lý riêng ký tự 'đ' và 'Đ' vì unicodedata không tự chuyển được
        text = re.sub(r'[đđ]', 'd', text)
        # 3. Loại bỏ các dấu thanh (huyền, sắc, hỏi, ngã, nặng) và dấu mũ (â, ê, ô, ơ, ư)
        text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
        # 4. Gom các khoảng trắng liên tiếp thành 1 khoảng trắng duy nhất
        text = re.sub(r'\s+', ' ', text)
        
        return text