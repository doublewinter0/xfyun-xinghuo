import base64

from iflygpt.exp import RequestError


# base64 解码
def decode(text: str):
    try:
        decoded_data = base64.b64decode(text).decode('utf-8')
        return decoded_data
    except Exception as e:
        raise RequestError(e)
