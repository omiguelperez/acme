from src.workflow.utils.abstracts import AbstractAuthenticationClass


class UserPINAuthenticationClass(AbstractAuthenticationClass):

    @classmethod
    def authenticate(cls, **credentials):
        ...
