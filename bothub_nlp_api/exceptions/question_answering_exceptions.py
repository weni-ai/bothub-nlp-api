class QuestionAnsweringException(Exception):
    pass


class EmptyInputException(QuestionAnsweringException):
    def __init__(self, message="Non-empty input is required."):
        self.message = message
        super().__init__(self.message)


class TokenLimitException(Exception):
    def __init__(self, text_overflow, message="Your text exceeds the limit of allowed tokens, please edit and try again") -> None:
        self.message = message
        self.text_overflow = text_overflow
        self.response = {
            "message": self.message,
            "text_overflow": self.text_overflow,
        }
        super().__init__(self.response)


class EmptyBaseException(QuestionAnsweringException):
    def __init__(self, message="Base text is inaccessible or nonexistent"):
        self.message = message
        super().__init__(self.message)


class LargeContextException(QuestionAnsweringException):
    def __init__(
        self, context_length, limit
    ):
        self.context_length = context_length
        self.limit = limit
        self.message = f"Invalid context length ({self.context_length} > {self.limit} characters)."
        super().__init__(self.message)

    def __str__(self):
        return f"{self.context_length} characters - {self.message}"


class LargeQuestionException(QuestionAnsweringException):
    def __init__(
        self, question_length, limit
    ):
        self.question_length = question_length
        self.limit = limit
        self.message = f"Invalid question length ({self.question_length} > {self.limit} characters)."
        super().__init__(self.message)

    def __str__(self):
        return f"{self.question_length} characters - {self.message}"
