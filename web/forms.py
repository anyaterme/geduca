from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _
from tinymce.widgets import TinyMCE
from ckeditor.widgets import CKEditorWidget


from web.models import *

class MessageForm(forms.ModelForm):
	#content = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 15}), required=False)
	content = forms.CharField(widget=CKEditorWidget())
	class Meta:
		model = Message
		fields = ['subject','content','status','priority','author','course']


class FileForm (forms.ModelForm):
	
	class Meta:
		model = File
		fields = ['file','name']

class ResourceFileForm(forms.ModelForm):
	file = forms.FileField(required=False)
	class Meta:
		model = ResourceFile

