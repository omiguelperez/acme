class WorkflowException(Exception):
    pass


class InvalidUserAccountCredentialsException(WorkflowException):
    pass


class InsufficientBalanceException(WorkflowException):
    pass
