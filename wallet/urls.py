from django.urls import path,include
from . import views

urlpatterns=[
    path('profile/',views.walletProfile,name="walletProfile"),
    path('profile/addMoney/',views.generateOtp,name="addMoney"),#addMoney
    path('profile/requestMoney/',views.requestMoney,name="requestMoney"),
    path('profile/acceptMoneyRequest/',views.generateOtp,name="acceptMoneyRequest"),#acceptMoneyRequest
    path('profile/deleteMoneyRequest/',views.deleteMoneyRequest,name="deleteMoneyRequest"),
    path('profile/cancelSentMoneyRequest/',views.cancelSentMoneyRequest,name="cancelSentMoneyRequest"),
    path('profile/sendMoney/',views.generateOtp,name="sendMoney"),#sendMoney
    path('profile/validateOtp/',views.validateOtp,name="validateOtp"),
    path('profile/deductMoney/',views.generateOtp,name="deductMoney")
]
