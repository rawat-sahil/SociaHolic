from django.db import models
from authentication.models import User
import pickle
from pyotp import TOTP
from FCS.settings import SECRET_KEY
# Create your models here.


class wallet(models.Model):
    username=models.ForeignKey(User,to_field='username',on_delete=models.CASCADE,unique=True)
    amount=models.TextField(default="1000")
    #in pending request each list will contain user that made request ,amount that need to be sent and the time when user made request
    pendingMoneyRequest=models.TextField(default='[]')

    transactionLimit=models.IntegerField(default=15)
    # in pending request each list will contain user that made request ,amount that need to be sent and the time when user made request
    sentMoneyRequest=models.TextField(default='[]')
    otp=models.TextField(blank=True)
    request=models.TextField(blank=True)

    def __str__(self):
        return self.username.username