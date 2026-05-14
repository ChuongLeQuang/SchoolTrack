import pytest
from apps.main_app.src.utils.core_name_matcher import NameMatcher


def test_normalize_for_strict_match() -> None:
    """
    EN: Test normalization (NFC, lowercase, whitespace removal) keeping accents.
    VI: Kiểm thử chuẩn hóa (NFC, chữ thường, bỏ khoảng trắng) nhưng giữ nguyên dấu.
    """
    # Xóa khoảng trắng thừa và ép chữ thường
    assert NameMatcher.normalize_for_strict_match("  Lê   Văn   Tám  ") == "lê văn tám"
    
    # Vẫn giữ nguyên dấu, phân biệt được Tâm và Tám
    assert NameMatcher.normalize_for_strict_match("Lê Văn Tám") != NameMatcher.normalize_for_strict_match("Lê Văn Tâm")


def test_compare_names_hybrid() -> None:
    """
    EN: Test the two-round hybrid name matching.
    VI: Kiểm thử bộ lọc so sánh tên kép (V1 và V2).
    """
    # Case 1: Giống hệt nhau (Khớp Vòng 1)
    is_match, match_type, score = NameMatcher.compare_names_hybrid("Lê Văn Tám", "Lê Văn Tám")
    assert is_match is True
    assert match_type == "V1_MATCH"

    # Case 2: DB mất dấu (Khớp Vòng 2)
    is_match, match_type, score = NameMatcher.compare_names_hybrid("Lê Văn Tám", "le van tam")
    assert is_match is True
    assert match_type == "V2_MATCH"

    # Case 3: Sai hoàn toàn (Trượt cả 2 vòng)
    is_match, match_type, score = NameMatcher.compare_names_hybrid("Lê Văn Tám", "Nguyễn Thị Hằng")
    assert is_match is False
    assert match_type == "NO_MATCH"