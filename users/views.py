from django.shortcuts import render,redirect ,HttpResponseRedirect,Http404
from django.urls import  reverse
from django.http import HttpResponse
from .models import user,group,userCategory,userUpgradeMoney
import json
# Create your views here.
def searchUser(request):
    #name to be searched
    name=request.POST.get("Friend and groups")


    searchResultUser=user.objects.filter(username=name)
    searchResultGroup=group.objects.filter(groupName=name)

    loggedInUser=request.user.username
    loggedInUserFriends=json.loads(user.objects.filter(username=loggedInUser)[0].friends)
    loggedInUserSentFriendRequest=json.loads(user.objects.filter(username=loggedInUser)[0].sentFriendRequests)
    loggedInUserPendingFriendRequests=json.loads(user.objects.filter(username=loggedInUser)[0].pendingFriendRequests)
    loggedInUserGroups=json.loads(user.objects.filter(username=loggedInUser)[0].userGroups)
    loggedInUserGroupAdmin=json.loads(user.objects.filter(username=loggedInUser)[0].groupAdmin)
    loggedInUserSentGroupRequest=json.loads(user.objects.filter(username=loggedInUser)[0].sentGroupRequests)

    usersToShow=[]
    groupsToShow=[]


    for i in searchResultUser:
        #this condition helps to search the users different from logged in users
        if i.username.username != request.user.username:
            #if user to be searched is in friend list
            if i.username.username in loggedInUserFriends:
                usersToShow.append([i.username.username,"Remove Friend"])

            #if user to be searched is in sent friend request
            elif i.username.username in loggedInUserSentFriendRequest:
                usersToShow.append([i.username.username,"Cancel Request"])

            #if user to be searched is in pending friend list
            elif i.username.username in loggedInUserPendingFriendRequests:
                usersToShow.append([i.username.username, "Accept Friend Request"])

            else :
                usersToShow.append([i.username.username, "Send Friend Request"])

    for i in searchResultGroup:
        # if the group is already joined by the logged in user
        if i.groupName in loggedInUserGroupAdmin:
            a=10
        elif (i.groupName in loggedInUserGroups) :
            groupsToShow.append([i.groupName,"leave group"])
        elif (i.groupName in loggedInUserSentGroupRequest):
            groupsToShow.append([i.groupName,"cancel request"])
        else :
            groupsToShow.append([i.groupName, "join group"])
    return render(request,"search friend or group.html",{'user':usersToShow,'groups':groupsToShow})

def sendFriendRequest(request):
    # toUser is the user to which the friend request has to be sent
    toUser=user.objects.filter(username=request.POST.get("searchedUser"))
    if len(toUser)== 0:
        return HttpResponse("toUser 0")
    toUser=toUser[0]

    #fromUser is the user from which the friend request is being sent
    fromUser=user.objects.filter(username=request.user.username)
    if len(fromUser)==0:
        return HttpResponse("fromUser 0")
    fromUser=fromUser[0]

    if(toUser.username.username in json.loads(fromUser.sentFriendRequests) or toUser.username.username in json.loads(fromUser.pendingFriendRequests)):
        return HttpResponse("user already in pending list or sent list")

    #adding the fromUser to pending friend request of toUser
    pendingFriendRequest=json.loads(toUser.pendingFriendRequests)
    pendingFriendRequest.append(fromUser.username.username)
    toUser.pendingFriendRequests=json.dumps(pendingFriendRequest)
    toUser.save()

    #adding the toUser to the sent friend request of the fromUser
    sentFriendRequest=json.loads(fromUser.sentFriendRequests)
    sentFriendRequest.append(toUser.username.username)
    fromUser.sentFriendRequests=json.dumps(sentFriendRequest)
    fromUser.save()


    return redirect(reverse('home'))

def cancelFriendRequest(request):
    # toUser is the user to which the friend request has to be sent
    toUser = user.objects.filter(username=request.POST.get("searchedUser"))
    if len(toUser) == 0:
        return Http404
    toUser = toUser[0]

    # fromUser is the user from which the friend request is being sent
    fromUser = user.objects.filter(username=request.user.username)
    if len(fromUser) == 0:
        return Http404
    fromUser = fromUser[0]

    # removing the fromUser to pending friend request of toUser
    pendingFriendRequest = json.loads(toUser.pendingFriendRequests)
    if(fromUser.username.username not in pendingFriendRequest):
        return HttpResponse("invalid request")
    pendingFriendRequest.remove(fromUser.username.username)
    toUser.pendingFriendRequests = json.dumps(pendingFriendRequest)


    # removing the toUser to the sent friend request of the fromUser
    sentFriendRequest = json.loads(fromUser.sentFriendRequests)
    if(toUser.username.username not in sentFriendRequest):
        return HttpResponse("invalid Request")
    sentFriendRequest.remove(toUser.username.username)
    fromUser.sentFriendRequests = json.dumps(sentFriendRequest)

    toUser.save()
    fromUser.save()

    return redirect(reverse('home'))

def addFriend(request):
    toUser = user.objects.filter(username=request.POST.get("searchedUser"))
    if len(toUser) == 0:
        return Http404
    toUser = toUser[0]

    # fromUser is the user from which the friend request is being sent
    fromUser = user.objects.filter(username=request.user.username)
    if len(fromUser) == 0:
        return Http404
    fromUser = fromUser[0]

    # removing the fromUser to pending friend request of toUser
    pendingFriendRequest = json.loads(fromUser.pendingFriendRequests)
    if(toUser.username.username not in pendingFriendRequest):
        return HttpResponse("invalid request")
    pendingFriendRequest.remove(toUser.username.username)
    fromUser.pendingFriendRequests = json.dumps(pendingFriendRequest)


    # removing the toUser to the sent friend request of the fromUser
    sentFriendRequest = json.loads(toUser.sentFriendRequests)
    if(fromUser.username.username not in sentFriendRequest):
        return HttpResponse("invalid request")
    sentFriendRequest.remove(fromUser.username.username)
    toUser.sentFriendRequests = json.dumps(sentFriendRequest)

    fromUser.save()
    toUser.save()

    # adding fromUser to toUser friend list
    toUserFriends=json.loads(toUser.friends)
    toUserFriends.append(fromUser.username.username)
    toUser.friends=json.dumps(toUserFriends)
    toUser.save()

    # adding toUser to fromUser friend list
    fromUserFriends=json.loads(fromUser.friends)
    fromUserFriends.append(toUser.username.username)
    fromUser.friends=json.dumps(fromUserFriends)
    fromUser.save()

    return redirect(reverse('home'))

def removeFriend(request):
    toUser = user.objects.filter(username=request.POST.get("searchedUser"))
    if len(toUser) == 0:
        return Http404
    toUser = toUser[0]

    # fromUser is the user from which the friend request is being sent
    fromUser = user.objects.filter(username=request.user.username)
    if len(fromUser) == 0:
        return Http404
    fromUser = fromUser[0]

    # adding fromUser to toUser friend list
    toUserFriends = json.loads(toUser.friends)
    toUserFriends.remove(fromUser.username.username)
    toUser.friends = json.dumps(toUserFriends)
    toUser.save()

    # adding toUser to fromUser friend list
    fromUserFriends = json.loads(fromUser.friends)
    fromUserFriends.remove(toUser.username.username)
    fromUser.friends = json.dumps(fromUserFriends)
    fromUser.save()

    return redirect(reverse('home'))


def joinGroup(request):
    return 0



def sendMessage(request):
    return 0


def pendingFriendRequest(request):
    loggedInUser= user.objects.filter(username= request.user.username)
    if(len(loggedInUser)==0):
        return HttpResponse("no logged in user")

    pendingRequests=json.loads(loggedInUser[0].pendingFriendRequests)
    return render(request,'pendingRequests.html',{'pendingRequests':pendingRequests})


def sentFriendRequest(request):
    loggedInUser=user.objects.filter(username=request.user.username)
    if(len(loggedInUser)==0):
        return HttpResponse("no logged in user")

    sentRequests=json.loads(loggedInUser[0].sentFriendRequests)


    return render(request,'sentRequests.html',{'sentRequests':sentRequests})


def friends(request):
    loggedInUser = user.objects.filter(username=request.user.username)
    if (len(loggedInUser) == 0):
        return HttpResponse("no logged in user")

    friendList = json.loads(loggedInUser[0].friends)

    return render(request, 'friends.html', {'friends': friendList})

def upgradeCategory(request):
    loggedInUser=user.objects.filter(username=request.user.username)
    if(len(loggedInUser)==0):
        return HttpResponse("user not found")

    loggedInUser=loggedInUser[0]
    currentCategory=loggedInUser.category
    return render(request,'upgradeCategory.html',{"userUpgradeMoney":userUpgradeMoney,"currentCategory":currentCategory})