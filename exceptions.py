class AIManagerBaseException(Exception):
    """
    Used as the base for all AIManager exceptions.
    """


class NonValidRole(AIManagerBaseException):
    """
    Raised when the role for a message is invalid.
    """