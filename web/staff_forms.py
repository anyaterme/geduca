from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _
from tinymce.widgets import TinyMCE


from web.models import *
from accounts.models import Profile


class CourseForm(forms.ModelForm):
	class Meta:
		model = Course
		fields = ['code','name','category','lapse','release_date','end_date','status','sb_link','aulatic_link','cep_link']

class CourseUserForm(forms.ModelForm):
	class Meta:
		model = CourseUser

class UserForm(forms.ModelForm):
	class Meta:
		model = User
		exclude =['is_superuser','is_staff','is_active','groups','user_permissions','last_login','date_joined']

class ProfileForm(forms.ModelForm):
	class Meta:
		model = Profile
		
class CategoryForm(forms.ModelForm):
	class Meta:
		model = Category

class CourseUserForm(forms.ModelForm):
	class Meta:
		model = CourseUser

from ckeditor.widgets import CKEditorWidget
class ChapterForm(forms.ModelForm):
	body = forms.CharField(widget=CKEditorWidget())
	right = forms.CharField(widget=CKEditorWidget())
	class Meta:
		model = Chapter
		exclude = ('order', 'name', 'parent', 'theme')

