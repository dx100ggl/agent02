from brain.c4.normalizers.section_normalizer import SectionNormalizer


def test_normalizer_empty():
    norm = SectionNormalizer()
    out = norm.normalize({})
    assert "market" in out
    assert "fundamentals" in out
