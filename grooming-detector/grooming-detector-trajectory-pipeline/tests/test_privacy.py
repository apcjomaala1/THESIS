import pytest

from privacy import redact_text


def test_redacts_common_direct_identifiers_with_typed_placeholders():
    raw = (
        "Email Name.Example+test@example.co.uk; call +63 917 123 4567; "
        "visit https://example.com/profile; IP 192.168.1.15; "
        "coordinates 14.5995, 120.9842; handles @my_handle and Gamer#1234; "
        "account 123456789012345678"
    )

    redacted = redact_text(raw)

    for marker in (
        "[EMAIL]",
        "[PHONE]",
        "[URL]",
        "[IP_ADDRESS]",
        "[COORDINATES]",
        "[HANDLE]",
        "[IDENTIFIER]",
    ):
        assert marker in redacted
    for sensitive_value in (
        "Name.Example+test@example.co.uk",
        "+63 917 123 4567",
        "https://example.com/profile",
        "192.168.1.15",
        "14.5995, 120.9842",
        "@my_handle",
        "Gamer#1234",
        "123456789012345678",
    ):
        assert sensitive_value not in redacted


def test_redaction_is_idempotent_and_preserves_benign_text():
    benign = "I have two cats and will join the game after dinner."
    assert redact_text(benign) == benign

    once = redact_text("Contact me at person@example.com or @person")
    assert redact_text(once) == once


def test_redaction_requires_a_string():
    with pytest.raises(TypeError):
        redact_text(None)
