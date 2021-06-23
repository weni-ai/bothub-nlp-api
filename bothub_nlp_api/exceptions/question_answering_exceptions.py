class QuestionAnsweringException(Exception):
    pass


class EmptyInputException(QuestionAnsweringException):
    def __init__(self, message="Non-empty input is required."):
        self.message = message
        super().__init__(self.message)


class LargeContextException(QuestionAnsweringException):
    def __init__(self, context_length, message="Invalid context length (over 25000 characters)."):
        self.context_length = context_length
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.context_length} characters - {self.message}'


class LargeQuestionException(QuestionAnsweringException):
    def __init__(self, question_length, message="Invalid question length (over 500 characters)."):
        self.question_length = question_length
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.question_length} characters - {self.message}'



