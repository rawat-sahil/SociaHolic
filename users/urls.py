from django.urls import path,include
from . import views

urlpatterns=[
    path('',views.searchUser,name='search'),
    path('sendFriendRequest/',views.sendFriendRequest,name='sendFriendRequest'),
    path('addFriend/',views.addFriend,name='addFriend'),
    # path('joinGroup/',views.joinGroup,name='joinGroup'),
    path('cancelFriendRequest',views.cancelFriendRequest,name='cancelFriendRequest'),
    path('removeFriend/',views.removeFriend,name="removeFriend"),
    # path('sendMessage/',views.sendMessage,name='sendMessage'),
    path('pendingFriendRequests/',views.pendingFriendRequest,name='pendingFriendRequest'),
    path('sentFriendRequests/',views.sentFriendRequest,name='sentFriendRequest'),
    path('friends/',views.friends,name='friends'),
    path('upgradeCategory/',views.upgradeCategory,name='upgradeCategory')
]