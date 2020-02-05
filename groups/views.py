from django.shortcuts import render,redirect
from django.http import  HttpResponse, HttpResponseRedirect
from users.models import user,groupLimit,userCategory,Casual
from users.models import group as GROUP
from wallet.models import wallet
import json
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
import codecs
import pickle
from pyotp import TOTP
from datetime import datetime
import base64
from django.urls import reverse
# Create your views here.

requestTypes=["join group"]
def generateOtp(request,loggedInUserProfile,groupSearched):
    ########Generation of otp and saving it in database
    loggedInUser=wallet.objects.filter(username=loggedInUserProfile.username.username)
    loggedInUser=loggedInUser[0]
    TOTPinput=str(datetime.now())
    TOTPinput=base64.b32encode(TOTPinput.encode())
    TOTPinput=TOTPinput.decode()
    totp=TOTP(TOTPinput)
    totp.interval=180
    otp=totp.now()
    loggedInUser.otp=codecs.encode(pickle.dumps(totp),"base64").decode()
    ##########################################################

    print("generate otp")
    print(otp)


    requestToBeSaved = []


    requestToBeSaved.append(requestTypes[0])
    requestToBeSaved.append(loggedInUser.username.username)
    requestToBeSaved.append(groupSearched.groupName)
    loggedInUser.request=json.dumps(requestToBeSaved)

    #####Sending email
    email_subject = 'Continue Payment'
    message = render_to_string('send_otp.html', {
        'otp':otp,
    })
    to_email = loggedInUser.username.email
    print(to_email)
    email = EmailMessage(email_subject, message, to=[to_email])
    email.send()
    ###################

    loggedInUser.save()
    return render(request,'groupOtp.html')

def GroupvalidateOtp(request):
    print(request.user.username)
    loggedInUser=wallet.objects.filter(username=request.user.username)
    if(len(loggedInUser)==0):
        return HttpResponse("invalid response")

    loggedInUser=loggedInUser[0]
    print(loggedInUser.otp)
    # print(loggedInUser.otp.decode)

    ######################################retrieve sent otp from database
    totp=pickle.loads(codecs.decode(loggedInUser.otp.encode(),"base64"))

    ##########################################################################

    try:
        otp=int(request.POST.get("otp"))
    except:
        return HttpResponse("invalid otp")

    print("validate otp")
    print(totp.now())
    print("entered otp   " + str(otp))
    print(totp.verify(str(otp)))
    print(totp.verify(str(otp)))
    boolean=totp.verify(str(otp))
    print(boolean)
    # print(type(totp.verify(str(otp))))
    if(boolean):
        print("verification done")
        ##########After verifying otp generate new otp so that old one cannot be used again
        TOTPinput = str(datetime.now())
        TOTPinput = base64.b32encode(TOTPinput.encode())
        TOTPinput = TOTPinput.decode()
        totp = TOTP(TOTPinput)
        totp.interval=180
        loggedInUser.otp = codecs.encode(pickle.dumps(totp), "base64").decode()
        loggedInUser.save()

        ################################################################


        ######retrive sent request from database
        requestToBeDone=json.loads(loggedInUser.request)
        print(str(requestToBeDone),"something new")
        #### request to done in format  (0)request type, (1)logged in user ,(2)amount,(3)requested user (4) time
        if(len(requestToBeDone)==0):
            return HttpResponse("OTP already used")


        if(requestToBeDone[0]==requestTypes[0]):####add money request
            groupSearched=GROUP.objects.filter(groupName=requestToBeDone[2])
            if(len(groupSearched)==0):
                return HttpResponse("group does not exist anymore")
            groupSearched=groupSearched[0]
            amountToBeDeducted=float(groupSearched.joiningFees)
            currentAmount=float(loggedInUser.amount)
            if(currentAmount<amountToBeDeducted):
                return HttpResponse("Insufficient balance")
            newAmount = str(currentAmount - amountToBeDeducted)
            loggedInUser.amount = newAmount
            loggedInUser.request = "[]"
            loggedInUser.save()
            loggedInUser.save()

            loggedInUser=user.objects.filter(username=request.user.username)
            loggedInUser=loggedInUser[0]
            loggedInUserGroups=json.loads(loggedInUser.userGroups)
            loggedInUserGroups.append(groupSearched.groupName)
            loggedInUser.userGroups=json.dumps(loggedInUserGroups)
            loggedInUser.save()
            groupSearchedMembers=json.loads(groupSearched.members)
            groupSearchedMembers.append(loggedInUser.username.username)
            groupSearched.members=json.dumps(groupSearchedMembers)
            groupSearched.save()

    ##########If otp is wrong make the current otp invalid
    TOTPinput = str(datetime.now())
    TOTPinput = base64.b32encode(TOTPinput.encode())
    TOTPinput = TOTPinput.decode()
    totp = TOTP(TOTPinput)
    totp.interval = 180
    loggedInUser.otp = codecs.encode(pickle.dumps(totp), "base64").decode()
    loggedInUser.save()

    ################################################################

    return redirect(reverse('home'))







def group(request):
    loggedInUser=user.objects.filter(username=request.user.username)
    if(len(loggedInUser)==0):
        return HttpResponse("no user found")

    loggedInUser=loggedInUser[0]

    createdGroups=json.loads(loggedInUser.groupAdmin)
    joinedGroups=json.loads(loggedInUser.userGroups)
    sentGroupRequest=json.loads(loggedInUser.sentGroupRequests)

    userCurrentCategory=loggedInUser.category
    try:
        maxGroupLimit=groupLimit[userCurrentCategory]
    except:
        print(userCurrentCategory,Casual)
        if(userCurrentCategory==Casual):
            maxGroupLimit=0
        else:
            return HttpResponse("not a valid user category")

    if (userCurrentCategory in userCategory) and(len(createdGroups) < maxGroupLimit):
        canCreateGroup=True

    else :
        canCreateGroup=False

    return render(request,'groups.html',{"createdGroups":createdGroups,"joinedGroups":joinedGroups,"sentGroupRequest":sentGroupRequest,"canCreateGroup":canCreateGroup})




def joinGroup(request):
    loggedInUser=user.objects.filter(username=request.user.username)
    print(request.POST.get('searchedGroup'))
    groupSearched= GROUP.objects.filter(groupName=request.POST.get('searchedGroup'))

    if(len(loggedInUser)==0):
        return HttpResponse("no user found")

    if(len(groupSearched)==0):
        return HttpResponse("no group found")

    loggedInUser=loggedInUser[0]
    groupSearched=groupSearched[0]
    if(float(groupSearched.joiningFees)==0):
        sentGroupRequest=json.loads(loggedInUser.sentGroupRequests)
        sentGroupRequest.append(groupSearched.groupName)
        groupPendingrequest=json.loads(groupSearched.pendingJoinRequests)
        groupPendingrequest.append(loggedInUser.username.username)

        loggedInUser.sentGroupRequests=json.dumps(sentGroupRequest)
        groupSearched.pendingJoinRequests=json.dumps(groupPendingrequest)
        loggedInUser.save()
        groupSearched.save()
        return redirect(reverse('home'))

    else :
        return generateOtp(request,loggedInUser,groupSearched)
    return HttpResponse("join group")

def groupProfile(request,groupName):
    loggedInUser=user.objects.filter(username=request.user.username)
    groupSearched=GROUP.objects.filter(groupName=groupName)
    if(len(loggedInUser)==0):
        return HttpResponse("no user found")

    if(len(groupSearched)==0):
        return HttpResponse("no group found")

    loggedInUser=loggedInUser[0]

    groupSearched=groupSearched[0]
    groupMembers=json.loads(groupSearched.members)
    groupAdmin=groupSearched.admin.username
    groupPrivacy=groupSearched.groupPrivacy
    groupPrivacyForMessage=groupPrivacy
    groupChat=json.loads(groupSearched.chat)
    groupPendingRequest=json.loads(groupSearched.pendingJoinRequests)
    isAdmin=(groupAdmin==loggedInUser.username.username)

    print(groupMembers)
    print(groupAdmin)

    if(loggedInUser.username.username not in groupMembers):
        return HttpResponse("Cannot Access Group")

    if(not groupPrivacy):
        if(groupAdmin==loggedInUser.username.username):
            groupPrivacyForMessage=True




    return render(request,'groupProfile.html',{"groupPendingRequest":groupPendingRequest,"groupMembers":groupMembers,"groupChat":groupChat,"groupName":groupName,"groupPrivacy":groupPrivacy,"groupPrivacyForMessage":groupPrivacyForMessage,"isAdmin":isAdmin})


def changeGroupPrivacy(request):
    loggedInUser=user.objects.filter(username=request.user.username)
    searchedGroup=GROUP.objects.filter(groupName=request.POST.get("groupName"))
    if(len(loggedInUser)==0):
        return HttpResponse("no user found")

    if(len(searchedGroup)==0):
        return HttpResponse("no group found")

    loggedInUser=loggedInUser[0]
    searchedGroup=searchedGroup[0]
    print(loggedInUser.username.username)
    print(searchedGroup.admin)
    if(loggedInUser.username.username != searchedGroup.admin.username):
        return HttpResponse("beta chalaki na dikha")

    groupPrivacy=False

    if(request.POST.get("privacy")=="All"):
        groupPrivacy=True

    elif(request.POST.get("privacy")=="Only Admin"):
        groupPrivacy=False

    else :
        return HttpResponse("invalid privacy request")

    searchedGroup.groupPrivacy=groupPrivacy
    searchedGroup.save()

    return redirect(reverse('group')+"groupProfile/"+str(searchedGroup.groupName))

def acceptGroupRequest(request):
    loggedInUser=user.objects.filter(username=request.user.username)
    searchedGroup=GROUP.objects.filter(groupName=request.POST.get("groupName"))
    searchedUser=user.objects.filter(username=request.POST.get("username"))
    if(len(loggedInUser)==0):
        return HttpResponse("invalid LoggedInuser")

    if(len(searchedGroup)==0):
        return HttpResponse("invalid group")

    if(len(searchedUser)==0):
        return HttpResponse("invalid Searcheduser")

    loggedInUser=loggedInUser[0]

    searchedUser=searchedUser[0]
    searchedUserSentRequest=json.loads(searchedUser.sentGroupRequests)

    searchedGroup=searchedGroup[0]
    groupPendingRequest=json.loads(searchedGroup.pendingJoinRequests)

    if(loggedInUser.username.username != searchedGroup.admin.username):
        return HttpResponse("user is not admin")

    if(searchedUser.username.username not in groupPendingRequest):
        return HttpResponse(" user not found in pending request")

    if(searchedGroup.groupName not in searchedUserSentRequest):
        return HttpResponse("group name not found in sent list")

    searchedUserSentRequest.remove(searchedGroup.groupName)
    searchedUser.sentGroupRequests=json.dumps(searchedUserSentRequest)
    searchedUserGroups=json.loads(searchedUser.userGroups)
    searchedUserGroups.append(searchedGroup.groupName)
    searchedUser.userGroups=json.dumps(searchedUserGroups)



    groupPendingRequest.remove(searchedUser.username.username)
    searchedGroup.pendingJoinRequests=json.dumps(groupPendingRequest)
    searchedGroupMembers=json.loads(searchedGroup.members)
    searchedGroupMembers.append(searchedUser.username.username)
    searchedGroup.members=json.dumps(searchedGroupMembers)

    searchedUser.save()
    searchedGroup.save()


    return redirect(reverse('home'))

def leaveGroup(request):
    loggedInUser = user.objects.filter(username=request.user.username)
    searchedGroup = GROUP.objects.filter(groupName=request.POST.get("searchedGroup"))

    if(len(loggedInUser)==0):
        return HttpResponse("invalid user")

    if(len(searchedGroup)==0):
        return  HttpResponse("invalid group")

    loggedInUser=loggedInUser[0]
    loggedInUserGroups=json.loads(loggedInUser.userGroups)
    searchedGroup=searchedGroup[0]
    searchedGroupMembers=json.loads(searchedGroup.members)

    if(loggedInUser.username.username not in searchedGroupMembers):
        return HttpResponse("user not in group")

    if(searchedGroup.groupName not in loggedInUserGroups):
        return HttpResponse("group not in the list")

    loggedInUserGroups.remove(searchedGroup.groupName)
    loggedInUser.userGroups=json.dumps(loggedInUserGroups)

    searchedGroupMembers.remove(loggedInUser.username.username)
    searchedGroup.members=json.dumps(searchedGroupMembers)

    loggedInUser.save()
    searchedGroup.save()



    return redirect(reverse('home'))

def cancelJoinRequest(request):
    loggedInUser=user.objects.filter(username=request.user.username)
    searchedGroup=GROUP.objects.filter(groupName=request.POST.get("group"))
    print(loggedInUser[0].username)
    print(searchedGroup[0].groupName)

    if(len(loggedInUser)==0):
        return HttpResponse("user not found")

    if(len(searchedGroup)==0):
        return HttpResponse("group not found")

    loggedInUser=loggedInUser[0]
    loggedInUserSentGroupRequest=json.loads(loggedInUser.sentGroupRequests)
    searchedGroup=searchedGroup[0]
    searchedGroupPendingRequest=json.loads(searchedGroup.pendingJoinRequests)

    if(loggedInUser.username.username not in searchedGroupPendingRequest):
        return HttpResponse("user not found in list")

    if(searchedGroup.groupName not in loggedInUserSentGroupRequest):
        return HttpResponse("group not found in list")

    loggedInUserSentGroupRequest.remove(searchedGroup.groupName)
    loggedInUser.sentGroupRequests=json.dumps(loggedInUserSentGroupRequest)

    searchedGroupPendingRequest.remove(loggedInUser.username.username)
    searchedGroup.pendingJoinRequests=json.dumps(searchedGroupPendingRequest)

    loggedInUser.save()
    searchedGroup.save()
    return redirect(reverse('home'))

def sendGroupMessage(request):
    loggedInUser=user.objects.filter(username=request.user.username)
    searchedGroup=GROUP.objects.filter(groupName=request.POST.get("groupName"))
    if(len(loggedInUser)==0):
        return HttpResponse("user not found")
    if(len(searchedGroup)==0):
        return HttpResponse("group not found")

    loggedInUser=loggedInUser[0]
    searchedGroup=searchedGroup[0]
    loggedInUserGroups = json.loads(loggedInUser.userGroups)
    searchedGroupMemebers=json.loads(searchedGroup.members)

    ###when anyone can send message in the group
    if(searchedGroup.groupPrivacy):
        if(loggedInUser.username.username not in searchedGroupMemebers):
            return HttpResponse("user not found in member list")

        if(searchedGroup.groupName not in loggedInUserGroups):
            return HttpResponse("group not found in userlist")

        groupChat=json.loads(searchedGroup.chat)
        groupChat.append(loggedInUser.username.username +" : "+ request.POST.get("message"))
        searchedGroup.chat=json.dumps(groupChat)

    else :
        if(loggedInUser.username.username == searchedGroup.admin.username):
            groupChat = json.loads(searchedGroup.chat)
            groupChat.append(loggedInUser.username.username +" : "+ request.POST.get("message"))
            searchedGroup.chat = json.dumps(groupChat)

        else:
            return HttpResponse("user is not admin")

    searchedGroup.save()
    return redirect(reverse('group')+"groupProfile/"+str(searchedGroup.groupName))



def createGroup(request):
    loggedInUser=user.objects.filter(username=request.user.username)
    if(len(loggedInUser)==0):
        return HttpResponse("user not found")

    loggedInUser=loggedInUser[0]
    createdGroups=json.loads(loggedInUser.groupAdmin)
    joinedGroups=json.loads(loggedInUser.userGroups)
    userCurrentCategory=loggedInUser.category
    try :
        maxGroupLimit=groupLimit[userCurrentCategory]

    except:
        if (userCurrentCategory == Casual):
            maxGroupLimit = 0
        else:
            return HttpResponse("not a valid user category")

    if((userCurrentCategory not in userCategory) or (len(createdGroups)==maxGroupLimit)):
        return HttpResponse("user category not found or max limit for creating group reached")

    try :
        groupJoiningPrice=float(request.POST.get("joiningCost"))
    except :
        return HttpResponse("not a valid cost")

    newGroup=GROUP(groupName=request.POST.get("Group Name"),admin=loggedInUser.username,joiningFees=str(groupJoiningPrice))
    newGroupMembers=json.loads(newGroup.members)
    newGroupMembers.append(loggedInUser.username.username)
    newGroup.members=json.dumps(newGroupMembers)

    createdGroups.append(newGroup.groupName)
    joinedGroups.append(newGroup.groupName)
    loggedInUser.groupAdmin=json.dumps(createdGroups)
    loggedInUser.userGroups=json.dumps(joinedGroups)

    newGroup.save()
    loggedInUser.save()

    return redirect(reverse('group'))








