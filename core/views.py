# pylint: disable=no-member
# pylint: disable=not-an-iterable
from django.shortcuts import render
from core.forms import UserForm
from .models import UserProfileInfo, Genre, Book, BookDonate
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.response import Response
from django.http import HttpResponseRedirect,HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.

#Creates user for a user node
@receiver(post_save, sender=UserProfileInfo, dispatch_uid='create_user_node')
def create_user_node(sender, instance, created, **kwargs):
    if created:
        user = User.objects.create_user(instance.username)
        user.set_password(instance.password)
        user.save()

#Deletes user from db when user node is deleted
@receiver(post_delete, sender=UserProfileInfo, dispatch_uid='delete_user_node')
def delete_user_node(sender, instance, **kwargs):
    User.objects.filter(username=instance.username).delete()

def user_login(request):
    if request.method=='POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username,password=password)
        if user:
            if user.is_active:
                login(request,user)
                print("successful")
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("ACCOUNT NOT ACTIVE")
        else:
            print("someone tried to login and failed")
            print("Username:{} and password {}".format(username,password))
            return HttpResponse("invalid login details")
    else:
        return render(request,'core/login.html',{})

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

def register(request):
    
    if request.method=='POST':
        userform = UserForm(data=request.POST)
        genresList = request.POST.getlist('genres')
        if userform.is_valid():
            newUser = userform.save(commit=False)
            newUser.latitude = request.POST.get('latitude')
            newUser.longitude = request.POST.get('longitude')
            newUser.save()
            print(newUser.latitude)
            print(request.POST.get('latitude'))
            print(newUser.longitude)
            for g in genresList:
                #print(g)
                newUser.favGenres.connect(Genre.nodes.get(name=g))
            return HttpResponseRedirect(reverse('index'))
        else:
            print(userform.errors)

    else:
        #createGenreNodes(request)
        user = request.user
        if user.is_authenticated:
            return HttpResponse('You are already logged in.')
        userform = UserForm()
        genreNodes = Genre.nodes
        return render(request,'core/register.html',{'userform':userform,'genreNodes':genreNodes})

def explore(request):
    books = Book.nodes
    booksToBePassed = []
    user = request.user
    if user.is_authenticated:
        userNode = UserProfileInfo.nodes.get(username=user.username)
        userGenres = userNode.favGenres.all()
        print(userGenres)
        #adding books belonging to user's genres
        for b in books:
            if b.wrote.get_or_none() != None and b.published.get_or_none() != None and b.genre.get_or_none() != None and b.genre.get() in userGenres:
                booksToBePassed.append([b.title,b.yearOfRelease,b.rating,b.wrote.get(),b.published.get(),b.image_url,b.genre.all()])
    else:    
        #adding all books in db
        for b in books:
            if b.wrote.get_or_none() != None and b.published.get_or_none() != None and b.genre.get_or_none() != None:
                booksToBePassed.append([b.title,b.yearOfRelease,b.rating,b.wrote.get(),b.published.get(),b.image_url,b.genre.all()])
            
    return render(request, 'core/explore.html', { 'books': booksToBePassed })

def donate(request):
    if request.method=='POST':
        user = request.user
        book = Book(title=request.POST.get('title'),img_url=request.POST.get('img_url'),yearOfRelease=request.POST.get('yearOfRelease'),rating=request.POST.get('rating'))
        book.save()
        userNode = UserProfileInfo.nodes.get(username=user.username)
        bookdonateObj = BookDonate()
        bookdonateObj.save()
        bookdonateObj.bookDonate.connect(book)
        bookdonateObj.user.connect(userNode)
        
        genresList = request.POST.getlist('genres')
        for g in genresList:
            book.genre.connect(Genre.nodes.get(name=g))
        return HttpResponseRedirect(reverse('index'))

    else:
        if request.user==None or request.user.is_authenticated==False:
            return register(request)
        else:
            genreNodes = Genre.nodes
            return render(request,'core/donate.html',{'genreNodes':genreNodes})

def findabenefactor(request):

    bookDonateObjs = BookDonate.nodes
    list = []
    for o in bookDonateObjs:
        list.append([o.bookDonate.get(),o.user.get()])
    return render(request,'core/findabenefactor.html',{'list':list})

def profile(request):
    node = UserProfileInfo.nodes.get(username=request.user.username)
    return render(request,'core/profile.html',{'latitude':node.latitude})

# Shows users what other users are reading who have common genres
def collab(request):
    books = Book.nodes
    booksToBePassed = []
    user = request.user
    if user.is_authenticated:
        userNode = UserProfileInfo.nodes.get(username=user.username)
        userGenres = userNode.favGenres.all()
        #print(userGenres)
        #adding books belonging to user's genres
        # for b in books:
        #     if b.wrote.get_or_none() != None and b.published.get_or_none() != None and b.genre.get_or_none() != None and b.genre.get() in userGenres:
        #         booksToBePassed.append([b.title,b.yearOfRelease,b.rating,b.wrote.get(),b.published.get(),b.image_url,b.genre.get_or_none()])
        
        #adding books belonging to common genres vale users
        commonUsers = []
        for g in userGenres:
            for curr in g.favGenre.all():
                if curr.username != user.username:
                    commonUsers.append(curr)
        #print(commonUsers)
        
        otherGenres = []
        for u in commonUsers:
            currGenres = u.favGenres.all()
            for cg in currGenres:
                if cg not in userGenres:
                    otherGenres.append(cg)

        #print(otherGenres)
        for b in books:
            if b.wrote.get_or_none() != None and b.published.get_or_none() != None and b.genre.get_or_none() != None and b.genre.get() in otherGenres:
                booksToBePassed.append([b.title,b.yearOfRelease,b.rating,b.wrote.get(),b.published.get(),b.image_url,b.genre.all()])
        
    else:    
        for b in books:
            if b.wrote.get_or_none() != None and b.published.get_or_none() != None and b.genre.get_or_none() != None:
                booksToBePassed.append([b.title,b.yearOfRelease,b.rating,b.wrote.get(),b.published.get(),b.image_url,b.genre.all()])
            
    return render(request, 'core/explore.html', { 'books': booksToBePassed })

#Creates genre nodes. Call each time before adding the first user. 
def createGenreNodes(request):
    genre = Genre(name="Fiction")
    genre.save()
    genre = Genre(name="Narrative")
    genre.save()
    genre = Genre(name="Novel")
    genre.save()
    genre = Genre(name="Non-Fiction")
    genre.save()
    genre = Genre(name="Mystery")
    genre.save()
    genre = Genre(name="Genre Fiction")
    genre.save()
    genre = Genre(name="Historical Fiction")
    genre.save()
    genre = Genre(name="Literary Fiction")
    genre.save()
    genre = Genre(name="Science Fiction")
    genre.save()
    genre = Genre(name="Biography")
    genre.save()
    genre = Genre(name="Poetry")
    genre.save()
    genre = Genre(name="Horror Fiction")
    genre.save()
    genre = Genre(name="Autobiography")
    genre.save()
    genre = Genre(name="Thriller")
    genre.save()
    genre = Genre(name="Memoir")
    genre.save()
    genre = Genre(name="Humour")
    genre.save()
    genre = Genre(name="Short Story")
    genre.save()
    genre = Genre(name="Fantasy")
    genre.save()
    genre = Genre(name="Performance Novel")
    genre.save()
    genre = Genre(name="Romance Novel")
    genre.save()
    genre = Genre(name="Historical Romance")
    genre.save()
    genre = Genre(name="Self-help book")
    genre.save()
    genre = Genre(name="Children's literature")
    genre.save()
    genre = Genre(name="Suspense")
    genre.save()
    genre = Genre(name="Fairy Tale")
    genre.save()
    genre = Genre(name="Essay")
    genre.save()
    genre = Genre(name="Article")
    genre.save()
    genre = Genre(name="Textbook")
    genre.save()
    genre = Genre(name="Prose")
    genre.save()
    genre = Genre(name="Young-adult Fiction")
    genre.save()
    genre = Genre(name="Science Fantasy")
    genre.save()
    genre = Genre(name="Adventure Fiction")
    genre.save()
    genre = Genre(name="Graphic Novel")
    genre.save()
    genre = Genre(name="Dictionary")
    genre.save()
    genre = Genre(name="Detective Fiction")
    genre.save()
    genre = Genre(name="Magical realism")
    genre.save()
    genre = Genre(name="Satire")
    genre.save()
    genre = Genre(name="Paranormal Romance")
    genre.save()
    genre = Genre(name="Myth")
    genre.save()
    genre = Genre(name="Legend")
    genre.save()
    genre = Genre(name="Fable")
    genre.save()
    genre = Genre(name="Encyclopedia")
    genre.save()
    genre = Genre(name="Picture Book")
    genre.save()
    genre = Genre(name="Drama")
    genre.save()
    genre = Genre(name="Narration")
    genre.save()
    genre = Genre(name="True Crime")
    genre.save()
    genre = Genre(name="High Fantasy")
    genre.save()
    genre = Genre(name="Speech")
    genre.save()
    genre = Genre(name="Crime Fiction")
    genre.save()
    genre = Genre(name="Cookbooks")
    genre.save()
    genre = Genre(name="signal_processing")
    genre.save()
    genre = Genre(name="data_science")
    genre.save()
    genre = Genre(name="mathematics")
    genre.save()
    genre = Genre(name="economics")
    genre.save()
    genre = Genre(name="history")
    genre.save()
    genre = Genre(name="science")
    genre.save()
    genre = Genre(name="psychology")
    genre.save()
    genre = Genre(name="computer_science")
    genre.save()
    genre = Genre(name="philosophy")
    genre.save()
    genre = Genre(name="comic")
    genre.save()

def index(request):
    return render(request,'core/index.html')

def aboutus(request):
    return render(request,'core/aboutus.html')

def contactus(request):
    return render(request,'core/contactus.html')

