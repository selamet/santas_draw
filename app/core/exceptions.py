class DrawServiceException(Exception):
    """Base exception for draw service operations"""
    pass


class InsufficientParticipantsError(DrawServiceException):
    """Raised when a draw has insufficient participants"""
    pass


class DrawAlreadyCompletedError(DrawServiceException):
    """Raised when attempting to execute an already completed draw"""
    pass


class DrawNotFoundError(DrawServiceException):
    """Raised when a draw is not found"""
    pass

