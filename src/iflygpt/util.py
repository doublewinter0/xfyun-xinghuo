import base64

from iflygpt.exp import IflyGPTError


# base64 decode
def decode(encoded_data: str, validate: bool = False) -> str:
    try:
        decoded_data = base64.b64decode(encoded_data, validate=validate).decode('utf-8')

        return decoded_data
    except Exception:
        raise IflyGPTError(encoded_data)
