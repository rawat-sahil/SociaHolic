from django.urls import path,include
from . import views
urlpatterns=[
    path('',views.chatFrontPage,name='chatList'),
    path('chatWindow/',views.chatWindow,name='chatWindow'),
    path('sendMessage/',views.sendMessage,name='sendMessage')
]