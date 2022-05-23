from django.contrib import admin

# Register your models here.
from .models import Post
#from .models import User


# class PostAdmin(admin.ModelAdmin):
#     readonly_fields = ('aaa')

admin.site.register(Post)
# admin.site.register(Menber)
# admin.site.register(User)
