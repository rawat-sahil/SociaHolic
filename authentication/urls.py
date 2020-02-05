from django.urls import path,include
from . import views
from django.conf.urls import url

urlpatterns=[
    path('',include('django.contrib.auth.urls')),
    path('signup/',views.userSignUp,name='signup'),
    path('activate/<uidb64>/<token>/',views.activate_account,name='activate')
]