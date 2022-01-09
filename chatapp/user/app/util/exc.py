class ChatNotFound (Exception):
    """
        Exception raised when the chatroom is not found on the database
    """

    def __init__ (self, chat_id: int = None) -> None:
        super().__init__(f"Chatroom {chat_id} not found")

class NotJobInstance (Exception):
    """
        Raised when a non-Job constructor is passed as a parameter to add Job to the dictionary
    """

    def __init__ (self) -> None:
        super().__init__(
            "Only classes inheriting from Job super class are allowed in the job queue"
        )

class MissingChatId (Exception):
    """
        Raised when it's not provided the chat id to build a job with priority 2
    """

    def __init__ (self) -> None:
        super().__init__(
            "Chat ID not provided for job with priority 2"
        )

class PriorityRangeError (Exception):
    """
        Raised when trying to access a job with priority outside the expected range
    """

    def __init__ (self) -> None:
        super().__init__(
            "Not expected priority to access the job object"
        )

class JobResolutionConfigurationError (Exception):
    """
        Raised when trying to specify chat ID without job priority equal to 2
    """

    def __init__ (self) -> None:
        super().__init__(
            "It's not allowed to specity chat ID with job priority different than 2"
        )