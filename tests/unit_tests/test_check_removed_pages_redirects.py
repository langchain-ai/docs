import sys

from scripts import check_removed_pages_redirects


def test_main_accepts_base_ref(monkeypatch) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "check_removed_pages_redirects.py",
            "--base-ref",
            "HEAD",
            "src/docs.json",
        ],
    )

    assert check_removed_pages_redirects.main() == 0
