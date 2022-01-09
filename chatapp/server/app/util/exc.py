class NotJobInstance (Exception):
    """
        Raised when a non-Job constructor is passed as a parameter to add Job to the dictionary
    """

    def __init__ (self) -> None:
        super().__init__(
            "Only classes inheriting from Job super class are allowed in the job queue"
        )

class PriorityRangeError (Exception):
    """
        Raised when trying to access a job with priority outside the expected range
    """

    def __init__ (self) -> None:
        super().__init__(
            "Not expected priority to access the job object"
        )

class UserDeviceNotFound (Exception):
    """
        Raised when the target user is not connected with any device to the server
    """

    def __init__ (self) -> None:
        super().__init__(
            "Target user is not connected to server"
        )