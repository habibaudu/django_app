from django.contrib.syndication.views import Feed
from app.models import Bookmark

class RecentBookmarks(Feed):
    title = 'Django Bookmarks | Recent Bookmarks'
    link = '/feeds/recent/'
    description = 'Recent bookmarks posted to django Bookmarks'

    def items(self):
        return Bookmark.objects.order_by('-id')[:10]

    def item_title(self, item):
        return item.title

    # def item_description(self, item):
    #     return item.description

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth.models import User

class UserBookmarks(Feed):
    def get_object(self,bits):
        if len(bits) !=1:
            raise ObjectDoestNotExist
        return User.objects.get(username = bits[0])

    def title(self,user):
        return 'Django Bookmarks | Bookmarks for %s'% user.username

    def link(self,user):
        return '/feeds/user/%s/' % user.username

    def description(self,user):
        return 'Recent Bookmarks Posted by %s' % user.username

    def items(self,user):
        return user.bookmark_set.order_by('-id')[:10]


    