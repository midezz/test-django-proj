from django.db import models
from django.contrib.auth.models import AbstractUser


class Inn(models.Model):
    number = models.CharField(max_length=12, unique=True)

    def __str__(self):
        return self.number


class CustomUser(AbstractUser):
    inn = models.ForeignKey(
        Inn,
        on_delete=models.SET_NULL,
        null=True,
        related_name='users'
    )
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)


class Transaction(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    out_user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='transactions')
    in_users = models.ManyToManyField(CustomUser)
