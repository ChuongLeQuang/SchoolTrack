import unicodedata
import re
import difflib
from typing import Tuple
from apps.main_app.src.utils.text_utils import TextUtils


class NameMatcher:
    """
    EN: Utility class for hybrid name matching to support Data Enrichment.
    VI: Lớp tiện ích so sánh tên kép hỗ trợ làm giàu dữ liệu.
    """

    @staticmethod
    def normalize_for_strict_match(text: str) -> str:
        """
        EN: Normalize unicode to NFC, convert to lowercase and remove extra spaces, keeping accents.
        VI: Chuẩn hóa Unicode về NFC, chuyển chữ thường và xóa khoảng trắng thừa, giữ nguyên dấu.
        """
        if not text:
            return ""
        text = str(text).lower().strip()
        text = re.sub(r'\s+', ' ', text)
        return unicodedata.normalize('NFC', text)

    @staticmethod
    def compare_names_hybrid(name1: str, name2: str) -> Tuple[bool, str, float]:
        """
        EN: Compare two names using a two-round hybrid approach (V1: keep accents, V2: remove accents).
        VI: So sánh hai tên sử dụng phương pháp kép (Vòng 1: giữ dấu, Vòng 2: gọt dấu).
        Returns a tuple: (is_match, match_type, score)
        """
        if not name1 or not name2:
            return False, "NO_MATCH", 0.0

        # Vòng 1: Xác thực ưu tiên (Giữ dấu, chuẩn hóa NFC)
        score_v1 = difflib.SequenceMatcher(None, NameMatcher.normalize_for_strict_match(name1), NameMatcher.normalize_for_strict_match(name2)).ratio()
        if score_v1 >= 0.95: return True, "V1_MATCH", score_v1

        # Vòng 2: Vớt vát (Gọt sạch dấu Tiếng Việt)
        score_v2 = difflib.SequenceMatcher(None, TextUtils.normalize_vietnamese(name1), TextUtils.normalize_vietnamese(name2)).ratio()
        if score_v2 >= 0.95: return True, "V2_MATCH", score_v2

        # Trượt cả 2 vòng
        return False, "NO_MATCH", max(score_v1, score_v2)