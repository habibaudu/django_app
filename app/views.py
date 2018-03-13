
from django.http import HttpResponse,Http404,HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.template.loader import get_template
from app.forms import * 
from django.shortcuts import render
from app.models import *
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist,MultipleObjectsReturned
from django.contrib import messages
from django.utils.translation import gettext as _
          
     
#main_page view

#create user_page view
from django.shortcuts import get_object_or_404
def user_page(request, username):
    user = get_object_or_404(User, username = username)

    bookmarks = user.bookmark_set.order_by('-id')
 
    variable = {
    'username':username,
    'bookmarks':bookmarks,
    'show_tags':True,
    'show_edit': username == request.user.username
    }

    return render(request,'user_page.html',variable)
	
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template

@login_required(login_url='/login/')
def friend_add(request):
     if 'username' in request.GET:
        friend = get_object_or_404(User,username = request.GET['username'])
        friendship = Friendship(from_friend = request.user, to_friend = friend)
        try:
           friendship.save()
           messages.add_message(request,messages.SUCCESS,'%s was added to your friend list.' % friend.username)
     
        except:
          messages.add_message(request,messages.WARNING,'%s is already a friend of yours.' % friend.username)
    
        return HttpResponseRedirect('/friends/%s/'% request.user.username)

     else :
        raise Http404


@login_required(login_url ='/login/')
def friend_invite(request):
    if request.method == 'POST':
       form = FriendInviteForm(request.POST)
       if form.is_valid():
          invitation = Invitation(
          name = form.cleaned_data['name'],
          email = form.cleaned_data['email'],
          code = User.objects.make_random_password(20),
          sender = request.user
          )
          invitation.save()
          try:
             invitation.send()
             messages.add_message(request, messages.SUCCESS,_('An invitation was sent to %(email)s.') % {
             'email': invitation.email})
          except:
             messages.add_message(request, messages.WARNING,_('There was an error while sending the invitation.'))
          
          return HttpResponseRedirect('/friend/invite/')
    else:
        form = FriendInviteForm()
        variables = {
        'form': form
        }
        return render(request,'friend_invite.html', variables)

def friend_accept(request, code):
    invitation = get_object_or_404(Invitation, code__exact=code)
    request.session['invitation'] = invitation.id
    return HttpResponseRedirect('/register/')
   


@login_required(login_url='/login/')
def bookmark_save_page(request):
  ajax = 'ajax' in request.GET
  if request.method == 'POST':
     form = BookmarkSaveForm(request.POST)
     if form.is_valid():
        bookmark = _bookmark_save(request,form)
        if ajax:
           variables = {
           'bookmarks': [bookmark],
           'show_edit': True,
           'show_tags': True
           }
           return render(request,'bookmark_list.html', variables)
        # else:
        #   variables = {
        #    'bookmarks': [bookmark],
        #    'show_edit': True,
        #    'show_tags': True
        #    }
        #   return render(request,'bookmark_list.html',variables)
        else:
          return HttpResponseRedirect('/user/%s/' % request.user.username)
     else:
        if ajax:
           return HttpResponse('failure')    
        
  elif 'url' in request.GET:
     url = request.GET['url']
     title =''
     tags = ''
     try:
       link = Link.objects.get(url = url)
       bookmark = Bookmark.objects.get(
         user = request.user,
         link = link
       )
       title = bookmark.title

       tags = ' '.join(tag.name for tag in bookmark.tags_set.all())

     except MultipleObjectsReturned:
       link = Link.objects.get(url = url)
       bookmark = Bookmark.objects.filter(
         user = request.user,
         link = link
       ).first()
       title = bookmark.title
       tags = ' '.join(tag.name for tag in bookmark.tags_set.all())
      

     form = BookmarkSaveForm({
       'url':url,
       'tags':tags,
       'title':title
      })
     return render(request,'bookmark_save.html',{'form':form})
  else:
    form = BookmarkSaveForm()
    variable = {'form' : form }
    return render(request,'bookmark_save.html',variable)
  if ajax:
    return render(request,
     'bookmark_save_form.html',
      variables
     )


def _bookmark_save(request,form):
    #get or create link
    link, dummy = Link.objects.get_or_create(
      url = form.cleaned_data['url']
    )

    #get or create bookmark

    bookmark, created = Bookmark.objects.get_or_create(
      user = request.user,
      link = link
    )
    
    #update of bookmark
    bookmark.title = form.cleaned_data['title']
    # if bookmark is being updated clear old tags
    if not created:
       bookmark.tags_set.clear()

    #create new tags
    tag_names = form.cleaned_data['tags'].split()

    for tag_name in tag_names:
        tag, dummy = Tags.objects.get_or_create(name = tag_name)
        bookmark.tags_set.add(tag)
    
    # share on the main page if requested
    if form.cleaned_data['share']:
       shared_bookmark, created =SharedBookmark.objects.get_or_create(bookmark = bookmark)
       if created:
          shared_bookmark.users_voted.add(request.user)
          shared_bookmark.save() 
    
    bookmark.save()
    return bookmark

@login_required(login_url='/login/')
def bookmark_vote_page(request):
    if "id" in request.GET:
       try:
          id = request.GET["id"]
          shared_bookmark = SharedBookmark.objects.get(id = id)
          user_voted = shared_bookmark.users_voted.filter(
            username = request.user.username
          )
          if not user_voted:
             shared_bookmark.votes +1
             shared_bookmark.users_voted.add(request.user)
             shared_bookmark.save()

       except ObjectDoesNotExist:
          raise Http404("Bookmark not found")

    if "HTTP_REFERER" in request.META:
       return HttpResponseRedirect(request.META['HTTP_REFERER'])
    return HttpResponseRedirect("/")

from datetime import datetime, timedelta
def popular_page(request):
    today = datetime.today()
    yesterday = today - timedelta(1)
    shared_bookmarks = SharedBookmark.objects.filter(date__gt = yesterday)
    shared_bookmarks = shared_bookmarks.order_by("-votes")[:10]
    variable ={ 'shared_bookmarks': shared_bookmarks }
    return render(request,'popular_page.html',variable)

def bookmark_page(request, bookmark_id):
    shared_bookmark = get_object_or_404(
      SharedBookmark, id=bookmark_id
      )

    variables = {
             'shared_bookmark': shared_bookmark
         }
    return render(request,'bookmark_page.html', variables)

def search_page(request):
    form = SearchForm()
    bookmarks = []
    show_results = False
    if 'query' in request.GET:
       show_results = True
       query = request.GET['query'].strip()
       if query:
          keywords = query.split()
          q = Q()
          for keyword in keywords:
             q = q & Q(title__icontains=keyword)
          form = SearchForm({'query' : query})
          bookmarks = Bookmark.objects.filter(q)[:10]
    variable = {
      'form' :form,
      'show_results':show_results,
      'bookmarks':bookmarks,
      'show_tags':True,
      'show_user':True
    }
    if 'ajax' in request.GET:
       return render(request,'bookmark_list.html',variable)
    else:
       return render(request,'search.html',variable)


from django.views.decorators.cache import cache_page
@cache_page
def tag_cloud_page(request):
    MAX_WEIGHT = 5
    tags = Tags.objects.order_by('name')
    #calculate tag, min and max count
    min_count = max_count = tags[0].bookmarks.count()
    for tag in tags:
       tag.count = tag.bookmarks.count()
       if tag.count < min_count:
          min_count = tag.count

       if tag.count < max_count:
          max_count =tag.count
    # calculate count range avoid dividing bi Zero
    range = float(max_count - min_count)
    if range == 0.0:
       range = 1.0

    #calculate tag weight

    for tag in tags:
       tag.weight = int(
         MAX_WEIGHT * (tag.count - min_count) /range
       )

    variable = {
      'tags':tags
    }

    return render(request,'tag_cloud_page.html',variable)

from django.shortcuts import get_object_or_404
def tag_page(request,tag_name):
    tag = get_object_or_404(Tags, name = tag_name)
    bookmarks = tag.bookmarks.order_by('-id')

    variable = {
        'tag_name':tag_name,
        'bookmarks':bookmarks,
        'show_tags':True,
        'show_user':True
    }

    return render(request,'tag_page.html',variable)

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import  redirect

from django.conf import settings
from django.contrib.auth import get_user_model
def register_page(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user=User.objects.create_user(username=username,email=email,password=password)
            if 'invitation' in request.session:
                # Retrieve the invitation object.
                invitation = \
                Invitation.objects.get(id=request.session['invitation'])
                # Create friendship from user to sender.
                friendship = Friendship(
                from_friend=user,
                to_friend=invitation.sender
                )
                friendship.save()
                # Create friendship from sender to user.
                friendship = Friendship (
                from_friend=invitation.sender,
                to_friend=user
                )
                friendship.save()
                # Delete the invitation from the database and session.
                invitation.delete()
                del request.session['invitation']
            if user:
               return HttpResponseRedirect('/register/success/')
            else:
               return HttpResponse('Registration failure')
        else :
           return render(request, 'registration/register.html',{'form':form})
    else:
        form = RegistrationForm()
        return render(request, 'registration/register.html',{'form':form})


def login_page(request):
    if request.method == 'POST':
       form = LoginForm(request.POST)
       if form.is_valid():
          username = form.cleaned_data.get('username')
          raw_pass = form.cleaned_data.get('password')
          user = authenticate(username = username, password = raw_pass)
          if user is not None:
            login(request, user) 
            return HttpResponseRedirect("/")
          else :
            return HttpResponse("Invalid Login details, username or password incorrect")
       else :
             return HttpResponse(" fill in all textfield ")
    else:

      form = LoginForm()
      variable = {
          'form':form
      }
      return render(request,"registration/login.html",variable)
          

      
#main_page view
def main_page(request):
   shared_bookmarks = SharedBookmark.objects.order_by('-date')[:10]
   variable = { 'shared_bookmarks': shared_bookmarks}
   return render(request,'main_page.html',variable)

#create user_page view
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator

def user_page(request, username):
    ITEMS_PER_PAGE = 3
    user = get_object_or_404(User, username = username)
    query_set = user.bookmark_set.order_by('-id')
    paginator = Paginator(query_set, ITEMS_PER_PAGE)
    is_friend = Friendship.objects.filter(
       from_friend=request.user,
       to_friend=user
    )
    try:
      page = int(request.GET.get('page'))
    except:
      page = 1
    try:
      bookmarks = paginator.get_page(page)
    except:
      raise Http404

    
    variable = {
    'username':username,
    'bookmarks':bookmarks,
    'show_tags':True,
    'show_edit': username == request.user.username,
    'show_paginator': paginator.num_pages > 1,
    'page': page,
    'pages': paginator.num_pages,
    'is_friend': is_friend,
    }

    return render(request,'user_page.html',variable)
# Create your views here.

def friends_page(request,username):
   user = get_object_or_404(User,username = username)
   friends = \
         [friendship.to_friend for friendship in user.friend_set.all()]

   friend_bookmarks = \
         Bookmark.objects.filter(user__in = friends).order_by('-id')

   variable = {
       'username': username,
       'friends': friends,
       'bookmarks': friend_bookmarks[:10],
       'show_tags': True,
       'show_user': True
   }

   return render(request,'friends_page.html',variable)

   #Add friend view

  

