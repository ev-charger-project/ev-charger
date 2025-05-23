import base64


def decode_base64(value: str) -> bytes:
    try:
        padding = "=" * (-len(value) % 4)
        value_with_padding = value + padding

        decoded_bytes = base64.b64decode(value_with_padding, validate=True)
        return decoded_bytes
    except (base64.binascii.Error, ValueError):
        return value.encode("utf-8")
