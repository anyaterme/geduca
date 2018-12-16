from django.contrib import admin, messages
from web.models import *
from modeltranslation.admin import TranslationAdmin
from accounts.models import *

import sys
reload(sys)
sys.setdefaultencoding("utf-8")


class ChapterAdmin(admin.ModelAdmin):
	list_display =("name", "id", "theme","order")

class MessageAdmin (admin.ModelAdmin):
	list_display = ("subject", "id", "course", "last_update")
	list_filter=('course',) 



admin.site.register(Category)
admin.site.register(Chapter, ChapterAdmin)
admin.site.register(Course)
admin.site.register(Message, MessageAdmin)
admin.site.register(File)
admin.site.register(Tag)
admin.site.register(Theme)
admin.site.register(CourseUser)
admin.site.register(ResourceFile)
#admin.site.register(Profile)
