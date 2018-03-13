"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os.path
from django.views.generic import  RedirectView,TemplateView
from django.contrib.auth.views import *
from django.conf.urls import include, url
from django.conf.urls import *
from app.views import *
from app.feeds import *
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static

admin.autodiscover()

urlpatterns = [
    # i18n
    re_path(r'^i18n/', include('django.conf.urls.i18n')),
    re_path(r'^feeds/(?P<url>.*)/$',RecentBookmarks()),
    re_path(r'^feeds/user/(\w+)/$',UserBookmarks()),
    re_path(r'^friends/(\w+)/$', friends_page),
    re_path(r'^friend/add/$', friend_add),
    re_path(r'^friend/invite/$',friend_invite),
    re_path(r'^friend/accept/(\w+)/$', friend_accept),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^login/$', login_page),
    re_path(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    re_path(r'^$',main_page),
     re_path(r'^user/(\w+)/$',user_page),
     re_path(r'^tag/([^/s]+)/$',tag_page),
     re_path(r'^tag/$', tag_cloud_page),
      re_path(r'^register/$',register_page),
      re_path(r'^search/$',search_page),
      re_path(r'^popular/$', popular_page),
      re_path(r'^comments/', include('django_comments.urls')),
      re_path(r'^password_change/$',auth_views.password_change),
      re_path(r'^save/$',bookmark_save_page),
      re_path(r'^vote/$',bookmark_vote_page),
      re_path(r'^bookmark/(\d+)/$', bookmark_page),
      re_path(r'^register/success/$', TemplateView.as_view(template_name="registration/register_success.html")), 
     
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


