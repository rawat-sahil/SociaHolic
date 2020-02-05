from django.urls import path,include
from . import views


urlpatterns=[
    path('userProfile/<username>/',views.profile,name='profile'),
    path('postDelete/',views.deletePost,name='deletePost'),
    path('post/',views.post,name='post'),
    path('postPrivacySetting/',views.postPrivacySetting,name="postPrivacySetting")

]