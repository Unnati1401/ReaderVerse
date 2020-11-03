# pylint: disable=no-member
# pylint: disable=not-an-iterable
from django.shortcuts import render
from core.forms import UserForm
from .models import UserProfileInfo, Genre, Book, Author
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
            for g in genresList:
                #print(g)
                newUser.favGenres.connect(Genre.nodes.get(name=g))
            message(request,'Registered successfully! You can login to proceed')
        else:
            print(userform.errors)
            message(request,'Error in registering. Please try again.')
    else:
        
        #createGenreNodes(request)
        user = request.user
        if user.is_authenticated:
            return HttpResponse('You are already logged in.')
        userform = UserForm()
        genreNodes = Genre.nodes
        return render(request,'core/register.html',{'userform':userform,'genreNodes':genreNodes})


def explore(request):
    books = []
    booksToBePassed = []
    user = request.user
    if user.is_authenticated:
        userNode = UserProfileInfo.nodes.get(username=user.username)
        userGenres = userNode.favGenres.all()
        #adding 5 books from user's genres
        for g in userGenres:
            count = 5
            for b in g.bookGenre.all():
                books.append(b)
                count = count - 1
                if count == 0:
                    break
        for b in books:
            booksToBePassed.append([b.Title, b.wrote.all(),b.img_url, b.genre.all()])
    else:    
        #adding 5 books from each genre
        genres = Genre.nodes.all()
        for g in genres:
            count = 5
            for b in g.bookGenre.all():
                books.append(b)
                count = count - 1
                if count == 0:
                    break
        for b in books:
            booksToBePassed.append([b.Title, b.wrote.all(),b.img_url, b.genre.all()])
                
    return render(request, 'core/explore.html', {'books': books})

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
        #adding books belonging to common genres vale users
        commonUsers = []
        for g in userGenres:
            for curr in g.favGenre.all():
                if curr.username != user.username:
                    commonUsers.append(curr)
        
        otherGenres = []
        for u in commonUsers:
            currGenres = u.favGenres.all()
            for cg in currGenres:
                if cg not in userGenres:
                    otherGenres.append(cg)

        for g in otherGenres:
            count = 5
            for b in g.bookGenre.all():
                books.append(b)
                count = count - 1
                if count == 0:
                    break

        for b in books:
            booksToBePassed.append([b.Title, b.wrote.all(),b.img_url, b.genre.all()])
        
    else:    
        #adding 5 books from each genre
        genres = Genre.nodes.all()
        for g in genres:
            count = 5
            for b in g.bookGenre.all():
                books.append(b)
                count = count - 1
                if count == 0:
                    break
        for b in books:
            booksToBePassed.append([b.Title, b.wrote.all(), b.img_url, b.genre.all()])
            
    return render(request, 'core/explore.html', { 'books': booksToBePassed })


def genresPage(request):

    genres = Genre.nodes
    if request.method == "POST":
        books = []
        booksToBePassed = []
        userGenres = []
        genresList = request.POST.getlist('genres')
        for g in genresList:
            userGenres.append(Genre.nodes.get(name=g))
        
        #adding books belonging to user selected genres
        for g in userGenres:
            count = 5
            for b in g.bookGenre.all():
                books.append(b)
                count = count - 1
                if count == 0:
                    break
        for b in books:
            booksToBePassed.append([b.Title, b.wrote.all(), b.img_url, b.genre.all()])
            
        return render(request, 'core/genresPage.html', {'books': booksToBePassed, 'genreNodes': genres})
    
    else:
        return render(request, 'core/genresPage.html', {'genreNodes': genres})


def authorsPage(request):
    authors = Author.nodes
    authorNodes = sorted(authors, key=lambda x: x.name, reverse=True)
    if request.method == "POST":
        books = []
        booksToBePassed = []
        userAuthors = []
        authorsList = request.POST.getlist('authors')
        for a in authorsList:
            userAuthors.append(Author.nodes.get(name=a))
        #adding books belonging to user's genres
        for a in userAuthors:
            count = 5
            for b in a.wrote.all():
                books.append(b)
                count = count - 1
                if count == 0:
                    break
        for b in books:
            booksToBePassed.append([b.Title, b.wrote.all(), b.img_url, b.genre.all()])
        
        return render(request, 'core/authorsPage.html', {'books': booksToBePassed, 'authorNodes': authorNodes})
    else:
        return render(request, 'core/authorsPage.html', {'authorNodes': authorNodes})

def message(request, message):
    return render('core/message.html',{'message':message})
# def publishersPage(request):
#     publishers = Publisher.nodes
#     if request.method == "POST":
#         books = Book.nodes
#         booksToBePassed = []
#         userPublishers = []
#         publishersList = request.POST.getlist('publishers')
#         for p in publishersList:
#             userPublishers.append(Publisher.nodes.get(name=p))
#         #adding books belonging to user's genres

#         for b in books:
#             if b.wrote.get_or_none() != None and b.published.get_or_none() != None and b.genre.get_or_none() != None and b.published.get_or_none() in userPublishers:
#                 booksToBePassed.append([b.title, b.yearOfRelease, b.rating, b.wrote.get(
#                 ), b.published.get(), b.image_url, b.genre.all()])

#         return render(request, 'core/publishersPage.html', {'books': booksToBePassed, 'publisherNodes': publishers})
#     else:
#         return render(request, 'core/publishersPage.html', {'publisherNodes': publishers})

#Creates genre nodes. Call each time before adding the first user. 
def createGenreNodes(request):
    genre = Genre(genre_id=0,name="Arts & Photography")
    genre.save()
    genre = Genre(genre_id = 1,name="Biographies & Memoirs")
    genre.save()
    genre = Genre(genre_id = 2,name="Business & Money")
    genre.save()
    genre = Genre(genre_id = 3,name="Calendars")
    
    genre.save()
    genre = Genre(genre_id = 4,name="Children's Books")
    genre.save()
    genre = Genre(genre_id = 5,name="Comics & Graphic Novels")
    genre.save()
    genre = Genre(genre_id = 6,name="Computers & Technology")
    genre.save()
    genre = Genre(genre_id = 7,name="Cookbooks, Food & Wine")
    genre.save()
    genre = Genre(genre_id = 8,name="Crafts, Hobbies & Home")
    genre.save()
    genre = Genre(genre_id = 9,name="Christian Books & Bibles")
    genre.save()
    genre = Genre(genre_id = 10,name="Engineering & Transportationry")
    genre.save()
    genre = Genre(genre_id = 11,name="Health, Fitness & Dieting")
    genre.save()
    genre = Genre(genre_id = 12,name="History")
    genre.save()
    genre = Genre(genre_id = 13,name="Humor & Entertainment")
    genre.save()
    genre = Genre(genre_id = 14,name="Law")
    genre.save()
    genre = Genre(genre_id = 15,name="Literature & Fiction")
    genre.save()
    genre = Genre(genre_id = 16,name="Medical Books")
    genre.save()
    genre = Genre(genre_id = 17,name="Mystery, Thriller & Suspense")
    genre.save()
    genre = Genre(genre_id = 18,name="Parenting & Relationships")
    genre.save()
    genre = Genre(genre_id = 19,name="Politics & Social Sciences")
    genre.save()
    genre = Genre(genre_id = 20,name="Reference")
    genre.save()
    genre = Genre(genre_id = 21,name="Religion & Spirituality")
    genre.save()
    genre = Genre(genre_id = 22,name="Romance")
    genre.save()
    genre = Genre(genre_id = 23,name="Science & Math")
    genre.save()
    genre = Genre(genre_id = 24,name="Science Fiction & Fantasy")
    genre.save()
    genre = Genre(genre_id = 25,name="Self-Help")
    genre.save()
    genre = Genre(genre_id = 26,name="Sports & Outdoors")
    genre.save()
    genre = Genre(genre_id = 27,name="Teen & Young Adult")
    genre.save()
    genre = Genre(genre_id = 28,name="Test Preparation")
    genre.save()
    genre = Genre(genre_id = 29,name="Travel")
    genre.save()
    genre = Genre(genre_id = 30,name="Gay & Lesbian")
    genre.save()
    genre = Genre(genre_id = 31,name="Education & Teaching")
    genre.save()
    

def index(request):
    return render(request,'core/index.html')

def aboutus(request):
    return render(request,'core/aboutus.html')

def contactus(request):
    return render(request,'core/contactus.html')
