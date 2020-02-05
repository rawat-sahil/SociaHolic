from django.db import models
from authentication.models import User
# Create your models here.


class chatDB(models.Model):
    username=models.ForeignKey(User,to_field='username',on_delete=models.CASCADE,unique=True)
    chat=models.TextField(default='{}')

    def __str__(self):
        return self.username.username