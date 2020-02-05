from django.shortcuts import render,redirect
from users.models import user
from django.http import  HttpResponse,Http404
from users.models import user
from django.urls import reverse
import json
from datetime import datetime
# Create your views here.


def profile(request,username):
    # print(username)
    # print(request.user.username)
    if(len(user.objects.filter(username=username))==0 or len(user.objects.filter(username=request.user.username))==0):
        return HttpResponse("page not found")
    userProfile=user.objects.filter(username=username)
    print(userProfile[0].post)
    posts=json.loads(userProfile[0].post)
    loggedInUser=request.user.username
    postPrivacy=userProfile[0].postPrivacy
    if(postPrivacy==True):
        postPrivacy="friends"
    else:
        postPrivacy="only me"
    return render(request,'profile.html',{'username':username,'posts':posts,'loggedInUser':loggedInUser,"privacySetting":postPrivacy,"email":userProfile[0].username.email})


def checkFriends(postingUser , profileUser):
    postingUserFriends=json.loads(postingUser[0].friends)
    profileUserFriends=json.loads(profileUser[0].friends)
    if((profileUser[0].username.username in postingUserFriends) and (postingUser[0].username.username in profileUserFriends)):
        return True

    return False

def post(request):
    print("enter post")
    postingUser=user.objects.filter(username=request.user.username)
    profileUser=user.objects.filter(username= request.POST.get("profileUser"))
    # print(request.POST.get("profileUser"))
    # print(request.user.username)
    if(len(postingUser)==0 or len(profileUser)==0):
        return HttpResponse("page not founddddd")

    #defaul post privacy in false which means only user can post and friends cannot post on the timeline
    postPrivacy=profileUser[0].postPrivacy

    #adding now time to the post to be posted so that it is easy to identify uniquely while deleting the post
    now=datetime.now()
    now=now.strftime("%d/%m/%Y %H:%M:%S")

    if(postPrivacy and checkFriends(postingUser,profileUser)):
        posts=json.loads(profileUser[0].post)
        posts.append(request.POST.get("toBePosted")+" "+now)
        profileUser[0].post=json.dumps(posts)
        profileUser[0].save()
        return redirect(reverse('profile',kwargs={'username':profileUser[0].username.username}))
    if(postingUser[0].username.username == profileUser[0].username.username):
        posts = json.loads(profileUser[0].post)
        posts.append(request.POST.get("toBePosted")+" "+now)
        profileUser[0].post = json.dumps(posts)
        profileUser[0].save()
        return redirect(reverse('profile',kwargs={'username':profileUser[0].username.username}))
    return HttpResponse("your friend has disabled posting on his/her profile")


def deletePost(request):
    print("enter delete post")
    loggedInUser=user.objects.filter(username=request.user.username)
    profileUser=user.objects.filter(username=request.POST.get("profileUser"))
    if(len(loggedInUser)==0 or len(profileUser)==0):
        return HttpResponse("page not found")

    if(loggedInUser[0].username.username!=profileUser[0].username.username):
        return HttpResponse("invalid request")

    postToBeDeleted=request.POST.get("post")
    posts=json.loads(loggedInUser[0].post)
    posts.remove(postToBeDeleted)
    loggedInUser[0].post=json.dumps(posts)
    loggedInUser[0].save()

    return redirect(reverse('profile',kwargs={'username':loggedInUser[0].username.username}))


def postPrivacySetting(request):
    loggedInUser = user.objects.filter(username=request.user.username)
    profileUser = user.objects.filter(username=request.POST.get("profileUser"))

    #if logged in user or profile user is not present in the user list
    if (len(loggedInUser) == 0 or len(profileUser) == 0):
        return HttpResponse("page not found")

    #if logged in user is not same as the user on whose profile changes are being made
    if (loggedInUser[0].username.username != profileUser[0].username.username):
        return HttpResponse("invalid request")

    privacyRequest=request.POST.get("postPrivacySetting")
    print(privacyRequest)
    if(privacyRequest=='friends'):
        loggedInUser[0].postPrivacy=True
        loggedInUser[0].save()
        return redirect(reverse('home'))

    elif(privacyRequest=='onlyMe'):
        loggedInUser[0].postPrivacy=False
        loggedInUser[0].save()
        return redirect(reverse('home'))

    else :
        return HttpResponse("invalid Request")