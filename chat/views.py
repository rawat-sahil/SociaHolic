from django.shortcuts import render,redirect
import json
from django.http import HttpResponse
from users.models import user,userCategory,commercial
from .models import chatDB
from django.urls import reverse
# Create your views here.

def chatFrontPage(request):
    loggedInUser=user.objects.filter(username=request.user.username)
    chat=chatDB.objects.filter(username=request.user.username)
    if(len(loggedInUser)==0):
        return HttpResponse("user not found")

    if(len(chat)==0):
        return HttpResponse("chat not found")

    loggedInUser=loggedInUser[0]
    isCommercial=loggedInUser.category==commercial
    chat=chat[0]

    friend=json.loads(loggedInUser.friends)
    chatFriends=json.loads(chat.chat).keys()
    print(chatFriends)
    friendList=list(set().union(friend,chatFriends))
    print(friendList)
    return render(request,'chatProfile.html',{'friendList':friendList,'isCommercial':isCommercial})

def chatWindow(request):
    print(type(request))
    loggedInUser=user.objects.filter(username=request.user.username)
    friendToChat=user.objects.filter(username=request.POST.get('friend'))
    if(len(loggedInUser)==0 or len(friendToChat)==0):
        return HttpResponse("here is problem user not found")

    loggedInUser=loggedInUser[0]
    isInUserCategory=loggedInUser.category in userCategory
    isCommercialUser=loggedInUser.category == commercial
    friendToChat=friendToChat[0]
    isInFriendList=friendToChat.username.username in json.loads(loggedInUser.friends)
    # chatDB object  of particular user
    loggedInUserChatDb = chatDB.objects.filter(username=loggedInUser.username.username)
    loggedInUserChatDb = loggedInUserChatDb[0]

    if((friendToChat.username.username not in list( set().union( json.loads(loggedInUser.friends) , json.loads(loggedInUserChatDb.chat).keys()))) and not(isCommercialUser)):
        return HttpResponse('friend not found')




    # all the chat of the user which is a dictionary
    loggedInUserAllChat=json.loads(loggedInUserChatDb.chat)

    # if never chatted before add the friend in the list
    if friendToChat.username.username not in loggedInUserAllChat.keys():
        loggedInUserAllChat[friendToChat.username.username]=[]
        # add new chat state in the chat db of particular user
        loggedInUserChatDb.chat=json.dumps(loggedInUserAllChat)
        loggedInUserChatDb.save()
        loggedInUserAllChat=json.loads(loggedInUserChatDb.chat)

    messages=loggedInUserAllChat[friendToChat.username.username]

    return render(request,'chatWindow.html',{'chat':messages,'friend':friendToChat.username.username,'isInUserCategory':isInUserCategory,'isCommercialUser':isCommercialUser,'isInFriendList':isInFriendList})

def sendMessage(request):
    loggedInUser = user.objects.filter(username=request.user.username)
    friendToChat = user.objects.filter(username=request.POST.get('friend'))
    print(friendToChat)
    print(loggedInUser)
    if (len(loggedInUser) == 0 or len(friendToChat) == 0):
        return HttpResponse("user or friend not found")

    # logged in user and the friend that you want to chat with
    loggedInUser = loggedInUser[0]
    friendToChat = friendToChat[0]
    isCommercial=loggedInUser.category==commercial
    if (friendToChat.username.username not in json.loads(loggedInUser.friends) and not(commercial)):
        return HttpResponse('friend not found')

    # chatDb objects of both the logged in user and friend
    loggedInUserChatDb=chatDB.objects.filter(username=loggedInUser.username.username)[0]
    friendChatDb=chatDB.objects.filter(username=friendToChat.username.username)[0]


    # logged in user all chats and friend all chats i.e. is in dictionary form
    loggedInUserAllChat=json.loads(loggedInUserChatDb.chat)
    friendAllChat=json.loads(friendChatDb.chat)
    if(loggedInUser.username.username not in friendAllChat.keys()):
        friendAllChat[loggedInUser.username.username]=[]
        friendChatDb.chat=json.dumps(friendAllChat)
        friendChatDb.save()
    friendAllChat=json.loads(friendChatDb.chat)

    if friendToChat.username.username not in loggedInUserAllChat.keys():
        loggedInUserAllChat[friendToChat.username.username] = []
        # add new chat state in the chat db of particular user
        loggedInUserChatDb.chat = json.dumps(loggedInUserAllChat)
        loggedInUserChatDb.save()
        loggedInUserAllChat = json.loads(loggedInUserChatDb.chat)

    # append the message in the logged in user chat and friend chat
    print(type(loggedInUserAllChat))
    loggedInUserAllChat[friendToChat.username.username].append('me :'+request.POST.get('message'))
    friendAllChat[loggedInUser.username.username].append(loggedInUser.username.username+" :" + request.POST.get('message'))

    # now after appending update the changes in database
    loggedInUserChatDb.chat=json.dumps(loggedInUserAllChat)
    friendChatDb.chat=json.dumps(friendAllChat)

    loggedInUserChatDb.save()
    friendChatDb.save()

    return redirect(reverse('chatList'))