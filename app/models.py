from __future__ import unicode_literals
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import get_template

# Create your models here.
@python_2_unicode_compatible

class Users(models.Model):
    username = models.CharField(max_length = 50 , unique = True)
    email = models.EmailField()
    password = models.CharField(max_length = 100)

    def __str__(self):
        return '%s ,%s' % (self.username, self.email)


class Link(models.Model):
    url = models.URLField(unique = True)
    def __str__(self):
        return self.url
  

class Bookmark(models.Model):
    title = models.CharField(max_length=200)
    user = models.ForeignKey(User,models.CASCADE)
    link = models.ForeignKey(Link,models.CASCADE)

    def __str__(self):
        return '%s, %s' % (self.user.username , self.link.url)

    def get_absolute_url(self):
        return self.link.url

   
class Tags(models.Model):
    name = models.CharField(max_length = 64 , unique = True)
    bookmarks = models.ManyToManyField(Bookmark)

    def __str__(self):
         return self.name


    # manipulate tags associated with a particular bookmark with tags_set becos of manito mani
    # to add bookmark.tags_set.all()
    # list of bookmarks associated with a tag  tag1.bookmarks.all()

class SharedBookmark(models.Model):
    bookmark = models.ForeignKey(Bookmark,models.CASCADE,unique =True)
    date = models.DateTimeField(auto_now_add =True)
    votes = models.IntegerField(default = 1)
    users_voted = models.ManyToManyField(User)

    def __str__(self):
         return "%s, %s" % (self.bookmark,self.votes)

class Friendship(models.Model):
    from_friend = models.ForeignKey(User,on_delete=models.CASCADE,related_name = 'friend_set')
    to_friend = models.ForeignKey(User,on_delete=models.CASCADE,related_name = 'to_friend_set')

    def __str__(self):
        return "%s, %s "% (self.from_friend.username, self.to_friend.username)

    class Meta:
        unique_together = (('from_friend', 'to_friend'),)

class Invitation(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    code = models.CharField(max_length=20)
    sender = models.ForeignKey(User,on_delete=models.CASCADE)
    def __str__(self):
        return '%s, %s' % (self.sender.username, self.email)

    def send(self):
        subject = 'Invitation to join Django Bookmarks'
        link = 'http://%s/friend/accept/%s/' % (
        settings.EMAIL_HOST,
        self.code
        )
        template = get_template('invitation_email.txt')
        context = {
        'name': self.name,
        'link': link,
        'sender': self.sender.username,
         }
        message = template.render(context)
        EmailMessage(
        subject, message,
        settings.EMAIL_HOST_USER, [self.email]
        )

    


