from django.db import models
from authentication.models import User
from math import inf
# Create your models here.



Casual="Casual"
premiumSilver="Premium Silver"
premiumGold="Premium Gold"
premiumPlatinum="Premium Platinum"
commercial="Commercial"

userCategory=[premiumSilver,premiumGold,premiumPlatinum,commercial]
userUpgradeMoney={premiumSilver:50,premiumGold:100,premiumPlatinum:150,commercial:5000}
transactionLimit={Casual:15,premiumSilver:30,premiumGold:30,premiumPlatinum:30,commercial:inf}
groupLimit={premiumSilver:2,premiumGold:4,premiumPlatinum:inf,commercial:inf}
class user(models.Model):
    username=models.ForeignKey(User,to_field='username' ,on_delete=models.CASCADE,unique=True)
    category=models.TextField(default=Casual)
    friends=models.TextField(default='[]')
    # list of all the groups the users is admin of

    groupAdmin=models.TextField(default='[]')
    userGroups = models.TextField(default='[]')
    sentGroupRequests=models.TextField(default='[]')

    ###post privacy default is false which means only user can post on timeline
    postPrivacy=models.BooleanField(default=False)
    post=models.TextField(default='[]')

    pendingFriendRequests=models.TextField(default='[]')
    sentFriendRequests=models.TextField(default='[]')

    def __str__(self):
        return self.username.username

class group(models.Model):
    groupName=models.TextField(unique=True)
    admin=models.ForeignKey(User,to_field='username',on_delete=models.CASCADE)
    joiningFees=models.TextField(default='0')

    pendingJoinRequests=models.TextField(default='[]')

    ### group privacy default is True which means any group member can send message in group
    groupPrivacy=models.BooleanField(default=True)

    ### invitation define whether the group can be joined or not
    Invitation=models.BooleanField(default=True)

    chat=models.TextField(default='[]')
    members=models.TextField(default='[]')

    def __str__(self):
        return self.groupName
