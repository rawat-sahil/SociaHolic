from django.urls import path,include
from . import views
urlpatterns=[
    path('groupProfile/<groupName>/',views.groupProfile,name='groupsProfile'),
    path('',views.group,name='group'),
    path('leaveGroup/',views.leaveGroup,name='leaveGroup'),
    path('joinGroup/',views.joinGroup,name='joinGroup'),
    path('sendGroupMessage/',views.sendGroupMessage,name='sendGroupMessage'),
    path('createGroup/',views.createGroup,name='createGroup'),
    path('cancelJoinRequest/',views.cancelJoinRequest,name='cancelJoinRequest'),
    path('changeGroupPrivacy/',views.changeGroupPrivacy,name='changeGroupPrivacy'),
    path('acceptGroupRequest/',views.acceptGroupRequest,name='acceptGroupRequest'),
    path('validateGroupOTP/',views.GroupvalidateOtp,name='groupValidateOTP'),
]