from django.contrib import admin
from app.models import *

# Register your models here.

class LinkAdmin(admin.ModelAdmin):
    pass
admin.site.register(Link,LinkAdmin)

class BookmarkAdmin(admin.ModelAdmin):
    list_display = ("title","user","link")
    list_filter = ("user",)
    search_fields = ("title",)
    ordering = ("title",)
    
admin.site.register(Bookmark,BookmarkAdmin)

class TagsAdmin(admin.ModelAdmin):
    pass
admin.site.register(Tags,TagsAdmin)

class SharedBookmarkAdmin(admin.ModelAdmin):
    pass
admin.site.register(SharedBookmark,SharedBookmarkAdmin)

class UsersAdmin(admin.ModelAdmin):
    pass
admin.site.register(Users,UsersAdmin)

class FriendshipAdmin(admin.ModelAdmin):
    pass
admin.site.register(Friendship,FriendshipAdmin)

class InvitationAdmin(admin.ModelAdmin):
    pass
admin.site.register(Invitation,InvitationAdmin)