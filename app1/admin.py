from django.contrib import admin
from .models import Member


class MemberAdmin(admin.ModelAdmin):
    list_display = ('username', 'email',)
    search_fields= ['username']


admin.site.register(Member,MemberAdmin)

# Register your models here.
