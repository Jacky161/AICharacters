class LLMManagerBaseException(Exception):
    """
    Used as the base for all AIManager exceptions.
    """


class NonValidRole(LLMManagerBaseException):
    """
    Raised when the role for a message is invalid.
    """


class MaxCtxWindow(LLMManagerBaseException):
    """
    Raised when the context window is exceeded by having the prompt be too large
    """
