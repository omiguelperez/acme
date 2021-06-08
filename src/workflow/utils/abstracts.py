class AbstractAuthenticationClass:

    @classmethod
    def authenticate(cls, **credentials):
        raise NotImplementedError
