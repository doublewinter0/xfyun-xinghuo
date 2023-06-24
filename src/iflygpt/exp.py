class IflyGPTError(Exception):
    """
    Base class for all Chatbot errors in this Project
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class LoginError(IflyGPTError):
    """
    Login error
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class AuthError(IflyGPTError):
    """
    Auth error
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class APIConnectionError(IflyGPTError):
    """
    APIConnectionError error
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class RequestError(APIConnectionError):
    """
    RequestError error
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
