from django.shortcuts import render,redirect
from django.urls import reverse
from .models import wallet
from django.http import HttpResponse
from math import inf
from datetime import datetime
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
import codecs
import pickle
from pyotp import TOTP
import json
from datetime import datetime
import base64
from users.models import userUpgradeMoney,user,userCategory
from users.models import transactionLimit as TL
# Create your views here.

requestTypes=["addMoney","acceptMoneyRequest","sendMoney","deductMoney"]

def generateOtp(request):
    loggedInUser=wallet.objects.filter(username=request.user.username)
    if(len(loggedInUser)==0):
        return HttpResponse("invalid user")
    loggedInUser=loggedInUser[0]
    if(loggedInUser.transactionLimit==0):
        return HttpResponse("Transaction limit for the month exhausted")
    ########Generation of otp and saving it in database
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

    #####################################################################3Saving request in database
    ##########structure of request: function ,logged in user ,amount, requested user
    requestToBeSaved = []
    print(dir(request))
    print(request.path)
    print(request.path_info)
    if(requestTypes[0] in request.path_info):#####for add money
        requestToBeSaved.append(requestTypes[0])
        requestToBeSaved.append(request.user.username)
        requestToBeSaved.append(request.POST.get("amountToBeAdded"))

    elif(requestTypes[1] in request.path_info):####for accept money request
        requestToBeSaved.append(requestTypes[1])
        requestToBeSaved.append(request.user.username)
        requestToBeSaved.append(request.POST.get("acceptRequestAmount"))
        requestToBeSaved.append(request.POST.get("acceptRequestUsername"))
        requestToBeSaved.append(request.POST.get("acceptRequestTime"))

    elif(requestTypes[2] in request.path_info):####for send Money
        requestToBeSaved.append(requestTypes[2])
        requestToBeSaved.append(request.user.username)
        requestToBeSaved.append(request.POST.get("amountToBeSend"))
        requestToBeSaved.append(request.POST.get("sendUsername"))

    elif(requestTypes[3] in request.path_info):####only for money deductions
        requestToBeSaved.append(requestTypes[3])
        requestToBeSaved.append(request.user.username)
        requestToBeSaved.append(request.POST.get("category"))

    loggedInUser.request=json.dumps(requestToBeSaved)
    ################################################################################################

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
    return render(request,'OTP input.html')

def validateOtp(request):
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
    print(type(totp.verify(str(otp))))
    if(totp.verify(str(otp))):
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
        print(requestToBeDone)
        #### request to done in format  (0)request type, (1)logged in user ,(2)amount,(3)requested user (4) time
        if(len(requestToBeDone)==0):
            return HttpResponse("OTP already used")


        if(requestToBeDone[0]==requestTypes[0]):####add money request
            print("add money enter")
            page= addMoney(requestToBeDone)
            return page

        elif(requestToBeDone[0]==requestTypes[1]):#### accept money request
            print("accept money enter")
            page= acceptMoneyRequest(requestToBeDone)
            return page

        elif(requestToBeDone[0]==requestTypes[2]):####sendMoney
            print("send money enter")
            page= sendMoney(requestToBeDone)
            return page

        elif(requestToBeDone[0]==requestTypes[3]):######for deduct money
            ###request format (0) request type (1) logged in user (2) userCategory
            print("deduct money enter")
            page=deductMoney(requestToBeDone)
            return page

        ####################################

    ##########If otp is wrong make the current otp invalid
    TOTPinput = str(datetime.now())
    TOTPinput = base64.b32encode(TOTPinput.encode())
    TOTPinput = TOTPinput.decode()
    totp = TOTP(TOTPinput)
    totp.interval = 180
    loggedInUser.otp = codecs.encode(pickle.dumps(totp), "base64").decode()
    loggedInUser.save()

    ################################################################

    return HttpResponse("invalid OTP")





def addMoney(request):

    loggedInUserWallet=wallet.objects.filter(username=request[1])
    if(len(loggedInUserWallet)==0):
        return HttpResponse("waller or user not found")

    loggedInUserWallet=loggedInUserWallet[0]
    try:
        amountToBeAdded=float(request[2])
    except:
        return HttpResponse("invalid amount")
    # print(type(amountToBeAdded))
    # print(amountToBeAdded)



    currentAmount=float(loggedInUserWallet.amount)
    newAmount=str(amountToBeAdded+currentAmount)
    loggedInUserWallet.amount=newAmount

    ##########for caller function
    loggedInUserWallet.request="[]"
    loggedInUserWallet.transactionLimit=loggedInUserWallet.transactionLimit-1
    #######################

    loggedInUserWallet.save()
    return redirect(reverse('walletProfile'))


def walletProfile(request):
    loggedInUserWallet=wallet.objects.filter(username=request.user.username)
    if(len(loggedInUserWallet)==0):
        return HttpResponse("wallet not found")

    loggedInUserWallet=loggedInUserWallet[0]
    amountInWallet=loggedInUserWallet.amount
    pendingMoneyRequest=json.loads(loggedInUserWallet.pendingMoneyRequest)
    sentMoneyRequests=json.loads(loggedInUserWallet.sentMoneyRequest)

    return  render(request,'walletProfile.html',{"amount":amountInWallet,"pendingMoneyrequest":pendingMoneyRequest,"sentMoneyRequest":sentMoneyRequests})

def requestMoney(request):
    now=datetime.now()
    now = now.strftime("%d/%m/%Y %H:%M:%S")
    loggerInUserWallet=wallet.objects.filter(username=request.user.username)
    requestedUserWallet=wallet.objects.filter(username=request.POST.get('requestUsername'))
    if(len(loggerInUserWallet)==0 or len(requestedUserWallet)==0):
        return HttpResponse("logged in user or requested user not found")

    loggerInUserWallet=loggerInUserWallet[0]
    requestedUserWallet=requestedUserWallet[0]
    requestedAmount=request.POST.get('amountToBeRequested')

    if(loggerInUserWallet.username.username==requestedUserWallet.username.username):
        return HttpResponse("you cannot request money to yourself")

    loggedInUserRequest=[]
    loggedInUserRequest.append(requestedUserWallet.username.username)
    loggedInUserRequest.append(str(float(requestedAmount)))
    loggedInUserRequest.append(now)

    requestedUserPending=[]
    requestedUserPending.append(loggerInUserWallet.username.username)
    requestedUserPending.append(str(float(requestedAmount)))
    requestedUserPending.append(now)

    print(loggedInUserRequest)
    print(requestedUserPending)

    newSentMoneyRequest=json.loads(loggerInUserWallet.sentMoneyRequest)
    newSentMoneyRequest.append(loggedInUserRequest)
    loggerInUserWallet.sentMoneyRequest=json.dumps(newSentMoneyRequest)
    newPendingMoneyRequest=json.loads(requestedUserWallet.pendingMoneyRequest)
    newPendingMoneyRequest.append(requestedUserPending)
    requestedUserWallet.pendingMoneyRequest=json.dumps(newPendingMoneyRequest)

    loggerInUserWallet.save()
    requestedUserWallet.save()

    return redirect(reverse('walletProfile'))


def acceptMoneyRequest(request):
    loggedInUserWallet = wallet.objects.filter(username=request[1])
    toSendUserWallet = wallet.objects.filter(username=request[3])
    if (len(loggedInUserWallet) == 0 or len(toSendUserWallet) == 0):
        return HttpResponse("logged in user or requested user not found")

    loggedInUserWallet=loggedInUserWallet[0]
    toSendUserWallet=toSendUserWallet[0]

    try:
        amountToBeSend=float(request[2])
    except :
        return HttpResponse("invalid amount")

    if(float(loggedInUserWallet.amount)<amountToBeSend):
       return  HttpResponse("sorry insufficient balance")

    timestamp=request[4]
    loggedInUserWallet.amount=str(float(loggedInUserWallet.amount)-amountToBeSend)
    toSendUserWallet.amount=str(float(toSendUserWallet.amount)+amountToBeSend)

    loggedInUserPending=[toSendUserWallet.username.username,str(amountToBeSend),timestamp]
    sendUserSent=[loggedInUserWallet.username.username,str(amountToBeSend),timestamp]
    print(loggedInUserPending)
    print(sendUserSent)

    newLoggedInUserPending=json.loads(loggedInUserWallet.pendingMoneyRequest)
    newLoggedInUserPending.remove(loggedInUserPending)
    loggedInUserWallet.pendingMoneyRequest=json.dumps(newLoggedInUserPending)

    newSendUserSent=json.loads(toSendUserWallet.sentMoneyRequest)
    newSendUserSent.remove(sendUserSent)
    toSendUserWallet.sentMoneyRequest=json.dumps(newSendUserSent)


    #####for caller function
    loggedInUserWallet.request="[]"
    loggedInUserWallet.transactionLimit=loggedInUserWallet.transactionLimit-1
    ####################################

    loggedInUserWallet.save()
    toSendUserWallet.save()

    return redirect(reverse('walletProfile'))


    return 0

def deleteMoneyRequest(request):
    loggedInUserWallet = wallet.objects.filter(username=request.user.username)
    requestedUserWallet = wallet.objects.filter(username=request.POST.get('deleteRequestUsername'))
    if (len(loggedInUserWallet) == 0 or len(requestedUserWallet) == 0):
        return HttpResponse("logged in user or requested user not found")

    loggedInUserWallet=loggedInUserWallet[0]
    requestedUserWallet=requestedUserWallet[0]

    deleteAmount=request.POST.get("deleteRequestAmount")
    timeStamp=request.POST.get("deleteRequestTime")

    loggedInUserPending=[]
    loggedInUserPending.append(requestedUserWallet.username.username)
    loggedInUserPending.append(deleteAmount)
    loggedInUserPending.append(timeStamp)

    requestedUserSent=[]
    requestedUserSent.append(loggedInUserWallet.username.username)
    requestedUserSent.append(deleteAmount)
    requestedUserSent.append(timeStamp)

    newSentMoneyRequest=json.loads(requestedUserWallet.sentMoneyRequest)
    newSentMoneyRequest.remove(requestedUserSent)
    requestedUserWallet.sentMoneyRequest=json.dumps(newSentMoneyRequest)

    newPendingRequest=json.loads(loggedInUserWallet.pendingMoneyRequest)
    newPendingRequest.remove(loggedInUserPending)
    loggedInUserWallet.pendingMoneyRequest=json.dumps(newPendingRequest)

    loggedInUserWallet.save()
    requestedUserWallet.save()

    return redirect(reverse('walletProfile'))

def cancelSentMoneyRequest(request):
    loggedInUserWallet = wallet.objects.filter(username=request.user.username)
    requestedUserWallet = wallet.objects.filter(username=request.POST.get('cancelRequestUsername'))
    if (len(loggedInUserWallet) == 0 or len(requestedUserWallet) == 0):
        return HttpResponse("logged in user or requested user not found")

    loggedInUserWallet = loggedInUserWallet[0]
    requestedUserWallet = requestedUserWallet[0]

    cancelRequestAmount=request.POST.get("cancelRequestAmount")
    timestamp=request.POST.get("cancelRequestTime")

    loggedInUserSent=[]
    loggedInUserSent.append(requestedUserWallet.username.username)
    loggedInUserSent.append(cancelRequestAmount)
    loggedInUserSent.append(timestamp)

    requestedPendingRequest=[]
    requestedPendingRequest.append(loggedInUserWallet.username.username)
    requestedPendingRequest.append(cancelRequestAmount)
    requestedPendingRequest.append(timestamp)

    newSentMoneyRequest=json.loads(loggedInUserWallet.sentMoneyRequest)
    newSentMoneyRequest.remove(loggedInUserSent)
    loggedInUserWallet.sentMoneyRequest=json.dumps(newSentMoneyRequest)

    newRequestMoneyPending=json.loads(requestedUserWallet.pendingMoneyRequest)
    newRequestMoneyPending.remove(requestedPendingRequest)
    requestedUserWallet.pendingMoneyRequest=json.dumps(newRequestMoneyPending)

    loggedInUserWallet.save()
    requestedUserWallet.save()

    return redirect(reverse('walletProfile'))


def sendMoney(request):
    loggedInUserWallet=wallet.objects.filter(username=request[1])
    toSendUserWallet=wallet.objects.filter(username=request[3])
    if (len(loggedInUserWallet) == 0 or len(toSendUserWallet) == 0):
        return HttpResponse("logged in user or requested user not found")

    loggedInUserWallet=loggedInUserWallet[0]
    toSendUserWallet=toSendUserWallet[0]

    if(loggedInUserWallet.username.username== toSendUserWallet.username.username):
        return HttpResponse("you cannot send money to yourself")

    print(request[2])
    try:
        amountToBeSend=float(request[2])
    except :
        return HttpResponse("invalid amount")

    if(float(loggedInUserWallet.amount)<amountToBeSend):
        return HttpResponse("sorry insufficient balance")

    loggedInUserWallet.amount=str(float(loggedInUserWallet.amount)-amountToBeSend)
    toSendUserWallet.amount=str(float(toSendUserWallet.amount)+amountToBeSend)

    ##############for caller function
    loggedInUserWallet.request="[]"
    loggedInUserWallet.transactionLimit=loggedInUserWallet.transactionLimit-1
   ############################


    loggedInUserWallet.save()
    toSendUserWallet.save()

    return redirect(reverse('walletProfile'))


def deductMoney(request):
    loggedInUserWallet = wallet.objects.filter(username=request[1])
    loggedInUser=user.objects.filter(username=request[1])
    if (len(loggedInUserWallet) == 0):
        return HttpResponse("waller or user not found")

    if(len(loggedInUser)==0):
        return HttpResponse("user not found")

    loggedInUser=loggedInUser[0]
    loggedInUserWallet = loggedInUserWallet[0]

    # check if the user category in input is same as we have in database
    if(request[2] in userCategory):
        loggedInUser.category=request[2]
        if(TL[loggedInUser.category]==inf):
            loggedInUserWallet.transactionLimit=100000
        else :
            loggedInUserWallet.transactionLimit=TL[loggedInUser.category]

    else:
        return HttpResponse("user category not found")

    try:
        amountToBeDeducted = float(userUpgradeMoney[request[2]])
    except:
        return HttpResponse("invalid amount")
    # print(type(amountToBeAdded))
    # print(amountToBeAdded)

    currentAmount = float(loggedInUserWallet.amount)
    if(currentAmount<amountToBeDeducted):
        return HttpResponse("Insufficient balance")

    newAmount = str(currentAmount-amountToBeDeducted)
    loggedInUserWallet.amount = newAmount

    ##########for caller function
    loggedInUserWallet.request = "[]"
    # loggedInUserWallet.transactionLimit=loggedInUserWallet.transactionLimit-1
    #######################

    loggedInUserWallet.save()
    loggedInUser.save()
    return redirect(reverse('home'))