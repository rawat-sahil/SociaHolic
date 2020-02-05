from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.urls import reverse
from .forms import Com_PageModelForm
from .models import Com_Page
from users.models import user,commercial

# Create your views here.

def create_view(request):

    loggedInUser=user.objects.filter(username=request.user.username)
    if(len(loggedInUser)==0):
        return HttpResponse("user not found")

    loggedInUser=loggedInUser[0]

    print("check condition",loggedInUser.category,commercial)
    if(loggedInUser.category != commercial):
        print("enter")
        return HttpResponse("you are not commercial user you cannot create pages")

    form=Com_PageModelForm(request.POST or None,request.FILES or None)
    if form.is_valid():
        form.instance.user=request.user
        form.save()
        return redirect(reverse('home'))

    context={'form':form}

    return render(request,'create.html',context)


def list_view(request):
    loggedInUser = user.objects.filter(username=request.user.username)
    if (len(loggedInUser) == 0):
        return HttpResponse("user not found")

    loggedInUser = loggedInUser[0]

    print("check condition", loggedInUser.category, commercial)
    if (loggedInUser.category != commercial):
        print("enter")
        return HttpResponse("you are not commercial user you cannot create pages")


    userPagesObjects=Com_Page.objects.filter(user=request.user.username)
    return render(request,'list.html',{"userPages":userPagesObjects})


def viewPage(request,page):
    userPageObject=Com_Page.objects.filter(url=page)
    if(len(userPageObject)==0):
        return HttpResponse("no page found")

    return render(request,'pageView.html',{'PageContent':userPageObject[0].content,'PageTitle':userPageObject[0].title})


def someRandomFunction(request):
    return HttpResponse("invalid url")