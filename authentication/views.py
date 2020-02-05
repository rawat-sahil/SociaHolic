from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login,authenticate
from .forms import UserSignUpForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .token_generator import account_activation_token
from .models import User
from django.core.mail import EmailMessage
############################
from users.models import user as USER
from wallet.models import wallet
from chat.models import chatDB
############################
# Create your views here.

def userSignUp(request):
    if request.method=='POST' :
        form=UserSignUpForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.is_active=False
            user.save()
            current_site=get_current_site(request)
            # print(user)
            # print(current_site.domain)
            # print(urlsafe_base64_encode(force_bytes(user.pk)))
            # print(account_activation_token)
            email_subject='Activate your account'
            message=render_to_string('activate_account.html',{
                'user':user,
                'domain':current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            to_email=form.cleaned_data.get('email')
            email=EmailMessage(email_subject,message,to=[to_email])
            email.send()
            return HttpResponse('We have sent you an email, please confirm your email address to complete registration')

    else:
        form=UserSignUpForm()
    return render(request,'signup.html',{'form':form})

def activate_account(request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    print(user.username)
    # print(user is not None)
    print(token)
    # print(account_activation_token.check_token(user,token))

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        newuser=USER(username=user)
        newuser.save()
        newWallet=wallet(username=user)
        newWallet.save()
        newChatDb=chatDB(username=user)
        newChatDb.save()
        login(request, user)
        return HttpResponse('Your account has been activate successfully.')
    else:
        return HttpResponse('Activation link is invalid!')