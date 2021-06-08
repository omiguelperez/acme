from factory.django import DjangoModelFactory

from src.workflow.models import User, Account


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User


class AccountFactory(DjangoModelFactory):
    class Meta:
        model = Account
