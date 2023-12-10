from chalice import ChaliceViewError

class BaseFailure(ChaliceViewError):
    default_message = 'Unkown failure.'

    def __init__(self, message=None):
            if message:
                super().__init__(message)
            else:
                super().__init__(self.default_message)
