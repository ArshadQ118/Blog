from django.contrib import admin
from Myapp.models import Contact, Profile, Posting, Comment
# Register your models here.


admin.site.register(Contact),
admin.site.register(Posting),
admin.site.register(Profile),
admin.site.register(Comment),
