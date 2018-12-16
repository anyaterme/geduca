import unicodedata
from django.db import models

from django.db import models
from django.contrib.auth.models import User  
from django.utils.translation import ugettext as _  
from userena.models import UserenaBaseProfile  
from tinymce.models import HTMLField
from web.models import *

def profile_file_name(instance, filename):
	instance.filename = filename
	return '/'.join(['media/users/',instance.user.id, datetime.datetime.now().strftime("%Y%m%d%H%M%S") + filename])

def attach_tag(obj, tag_str):
	clean = remove_accents(tag_str)
	try : 
		tag = Tag.objects.get(name=clean)

	except Tag.DoesNotExist:
		tag = Tag.objects.create(name=clean)
		tag.save()

	obj.tag.add(tag)


class Profile(UserenaBaseProfile):  
	user = models.OneToOneField(User,unique=True, verbose_name=_('user'),related_name='profile')
	phone = models.CharField(max_length=200, verbose_name=_("Telephone"),blank=True, default="")
	mobile_phone = models.CharField(max_length=200, verbose_name=_("Mobile phone"), blank=True, default="")
	description = HTMLField( verbose_name=_("Otros"),blank=True , default="")
	curriculum = HTMLField(verbose_name=_("Curriculum"),blank=True, default="")
	web_page = models.CharField(max_length=200, verbose_name=_("web page"), blank=True,default="")
	front_image = models.ImageField(upload_to=profile_file_name, blank = True, verbose_name=_('FRONT IMAGE'), help_text=_("Select a picture to upload"), null=True)
	tag = models.ManyToManyField(Tag, verbose_name=_("Search Tag"), related_name="tag_profile", null=True, help_text="Las etiquetas se asignan automaticamente al guardar",blank=True)

	def __unicode__(self):
		return "%s-%s"%( self.user.first_name, self.user.last_name)

	def save(self, *args, **kwargs):
            super(Profile, self).save(*args, **kwargs)
            first_name = self.user.first_name.split(" ")
            for item in first_name :
                    attach_tag(self, item)
            last_name = self.user.last_name.split(" ")
            for item in last_name:
                    attach_tag(self, item)
