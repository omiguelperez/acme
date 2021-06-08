from src.workflow.models import User, Account
from src.workflow.utils.abstracts import AbstractAuthenticationClass


class UserPINAuthenticationClass(AbstractAuthenticationClass):

    @classmethod
    def authenticate(cls, **credentials):
        try:
            user = User.objects.get(**credentials)
            account = user.account
            return {
                'balance': account.balance.to_decimal(),
                'is_valid': True,
                'user_id': user.user_id,
            }
        except (User.DoesNotExist, Account.DoesNotExist):
            return {
                'balance': None,
                'is_valid': False,
                'user_id': None,
            }

