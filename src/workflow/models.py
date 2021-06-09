from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from src.utils.models import ACMEModel


class User(ACMEModel):

    user_id = models.CharField(
        unique=True,
        max_length=17
    )

    pin = models.PositiveSmallIntegerField()

    def __str__(self):
        return _('User %(user_id)s') % {'user_id': self.user_id}


class Account(ACMEModel):

    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT
    )

    balance = models.DecimalField(
        default=Decimal(0),
        max_digits=17,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal(0)),
        ]
    )

    def __str__(self):
        return _('User %(user_id)s account with balance: %(balance)s') % {
            'user_id': self.user.user_id,
            'balance': self.balance,
        }


class Upload(ACMEModel):

    file = models.FileField(
        upload_to='workflow/files/'
    )
    success = models.BooleanField(default=False)
    logs = models.JSONField(default=list)
