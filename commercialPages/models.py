from django.db import models
from authentication.models import User
from django.urls import reverse
# Create your models here.

class Com_Page(models.Model):
    user=models.ForeignKey(User,to_field='username',on_delete=models.CASCADE)
    title=models.TextField(null=True,blank=False,unique=True)
    content=models.TextField(null=True,blank=False)
    url=models.TextField(null=True,blank=False,unique=True)
    timeStamp=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_delete_url(self):
        return reverse("pages:delete",kwargs={"id":self.id})

    def get_update_url(self):
        return reverse("pages:update",kwargs={"id":self.id})