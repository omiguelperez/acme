class WorkflowException(Exception):
    pass


class InvalidActionException(WorkflowException):
    pass


class InvalidUserAccountCredentialsException(WorkflowException):
    pass


class InsufficientBalanceException(WorkflowException):
    pass
