# -*- encoding: iso-8859-1 -*-
import unicodedata
import datetime
import hashlib
import json

from django.core.validators import RegexValidator
from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from geduca.settings import MEDIA_ROOT
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

from tinymce.models import HTMLField

from ckeditor.fields import RichTextField
from web.utils import *

# Create your models here.

COURSE_STATES = (('0',_('Desarrollo')),('1',_("Produccion")),('2','Terminado'))
MESSAGE_STATES = (
    ('0',_('Abierto')),
    ('1',_('Trabajando')),
    ('2',_('Resuelto')),
    ('3',_('Error')),
)

LAPSE = (('1314','2013-2014'),
            ('1415','2014-2015'),
            ('1516','2015-2016'),
            ('1617','2016-2017'),
            ('1718','2017-2018'),
            ('1819','2018-2019'),
            ('1920','2019-2020'),
            ('2021','2020-2021'),
            ('2122','2021-2022'),
            ('2223','2022-2023'))

MESSAGE_PRIORITY = (
    ('0',_("Normal")),
    ('1',_("Importante")),
    ('2',_("Urgente")),
)

FILE_TYPES = (
    ('doc',_('Documento Office')),
    ('docx',_("Documento Office 2007 o superior")),
    ('txt',_("Documento de texto")),
    ('pdf',_("Documento PDF")),
    ('jpg',_("Imagen JPG")),
    ('gif',_("Imagen gif")),
    ('png',_("Imagen png")),
    ('zip',_("Archivo comprimido zip"))

)

ROL =(( '0', "Staff"),
        ( '1', "Coordinador"),
        ( '2', "Tutor"))


def remove_accents(data):
    return unicodedata.normalize('NFKD', data).encode('ASCII', 'ignore').lower()
#    return ''.join(x for x in unicodedata.normalize('NFKD', data) if x in string.ascii_letters).lower()

def content_file_name(instance, filename):
    instance.filename = filename
    ext = filename[filename.rfind("."):]
    hash_str= filename + datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    name = hashlib.sha224(hash_str).hexdigest()[:30]
    name = name+ ext
#    return '/'.join(['media/courses/',instance.message.course.code, datetime.datetime.now().strftime("%Y%m%d%H%M%S") + filename])
    return '/'.join(['media/courses/',instance.message.course.code, name])

def resource_file_name(instance, filename):
    instance.filename = filename
    ext = filename[filename.rfind("."):]
    hash_str= filename + datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    name = hashlib.sha224(hash_str).hexdigest()[:30]
    name = name+ ext

#    return '/'.join(['media/resources/', datetime.datetime.now().strftime("%Y%m%d%H%M%S")+'-'+ filename])
    return '/'.join(['media/resources/', name ])

def content_image_name(instance, filename):
    instance.filename = filename
    path = 'media/courses/' + instance.chapter.theme.course.name + '/' + instance.chapter.theme.name + '/'
    return '/'.join(['media/courses/', instance.chapter.name, datetime.datetime.now().strftime("%Y%m%d%H%M%S") + filename])

class Base(models.Model):
    creation_date = models.DateTimeField('creation date', auto_now_add = True)
    modification_date = models.DateTimeField('modification date', auto_now = True)

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        print "Delete BASE"
        super(Base,self).delete(*args,**kwargs)

class Tag (Base):
    name = models.CharField(max_length=200, verbose_name=_("Nombre"))

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _("Etiqueta")
        verbose_name_plural = _('Etiquetas')
    
class Category (Base):
    code = models.CharField(max_length=50, verbose_name=_("Codigo"),unique=True, validators=[
        RegexValidator('^[a-zA-Z0-9_]{1,50}$',
            message=_("El codigo de la categoria solo puede contener letras numeros y guiones bajos")
        ),
    ])
    name = models.CharField(max_length=200, verbose_name=_("Nombre"))
    parent = models.ForeignKey("Category", verbose_name=_("Categoria Padre"), null=True, blank=True)
    manager = models.ManyToManyField(User,verbose_name=_("Administrador"))

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name =_("Categoria")
        verbose_name_plural = _("Categorias")
        ordering = ['name',]

class Course (Base):
    code = models.CharField(max_length=50, verbose_name=_("Codigo"),unique=True, validators=[
        RegexValidator('^[a-zA-Z0-9_./-]{1,50}$',
            message=_("El codigo del curso solo puede contener letras numeros y guiones bajos")
        ),
    ])
    name = models.CharField(max_length=200, verbose_name=_("Nombre"))
    category = models.ForeignKey(Category, verbose_name=_("Categoria"))
#    tutor = models.ManyToManyField(User,verbose_name=_("Tutores"),blank=True, null=True)
    lapse = models.CharField(choices=LAPSE,max_length=10,verbose_name=_("Course Lapse"),default="1415")
    release_date = models.DateField(_("Fecha de entrega"))
    end_date = models.DateField(_("Fecha Finalización"),default="9999-12-31")
    status = models.CharField(choices=COURSE_STATES, verbose_name=_("Estado"), max_length=10, default='0')
    sb_link= models.CharField(max_length=250, verbose_name=_("Enlace San Borondon "), default="", blank=True)
    aulatic_link= models.CharField(max_length=250, verbose_name=_("Enlace Aulatic"), default="",blank=True)
    cep_link = models.CharField(max_length=250, verbose_name=_("Enlace CEP"), default="",blank=True)
    tag = models.ManyToManyField(Tag, verbose_name=_("Search tag"), related_name="tag_course", null=True, help_text="Las etiquetas se asignan automaticamente al guardar")
    tutor_requestor = models.TextField(verbose_name=_("Tutor y Solicitante"), default="", blank=True)
    fix_parents = models.BooleanField(verbose_name=_("Fix Parents"),default=False)

    def __unicode__(self):
        return "%s-%s"%(self.code, self.name)

    
    def attach_tag(self, tag_str):
        clean = remove_accents(tag_str)
        try : 
            tag = Tag.objects.get(name=clean)
        except Tag.DoesNotExist:
            tag = Tag.objects.create(name=clean)
        tag.save()
        self.tag.add(tag)


    class Meta:
        verbose_name =_("Curso")
        verbose_name_plural=_("Cursos")

        
    def save(self, *args, **kwargs):
            super(Course, self).save(*args, **kwargs)    
            name = self.name.split(" ")
            for item in name :
                self.attach_tag (item)
            category = self.category.name.split(" ")
            for item in category:
                self.attach_tag(item)

#class CourseGuardian(Base):
#    name = models.CharField(max_length=200, verbose_name=_("Nombre"))
#    email = models.CharField(max_length=200, verbose_name=_("Email"))
#    phone = models.CharField(max_length=200, verbose_name=_("Phone"))
#
#    def __unicode__(self):
#        return "%s-%s"%(self.name, self.email)





class CourseUser(Base):
    user = models.ForeignKey(User, verbose_name=_("Usuario"),related_name="user_course")
    role = models.CharField(choices=ROL, max_length=20, verbose_name=_("Rol"))
    course = models.ForeignKey(Course, verbose_name=_("Course"),related_name="course_user")
    date = models.DateTimeField(blank=True,  auto_now = True, verbose_name=("Ultimo acceso"))

    def __unicode__(self):
        return "%s-%s"%( self.user.username, self.course.name)

    class Meta:
        unique_together=('user','course')
        verbose_name=_("Usuario del curso")
        verbose_name_plural =_("Usuarios del curso")

class Message(Base):
    subject = models.CharField(max_length=200, verbose_name=_("Asunto"), blank=True)
    content = HTMLField(blank=True)
    status = models.CharField(choices=MESSAGE_STATES, verbose_name=_("Estado"), max_length=10, default='0')
    priority= models.CharField(choices=MESSAGE_PRIORITY, verbose_name=_("Priority"), max_length=10,default='0')
    author = models.ForeignKey(User, verbose_name=_("Author"))
    course = models.ForeignKey(Course, verbose_name=_("Curso"), related_name=_("course_messages"))
    published = models.BooleanField(verbose_name=_("Publicado"),default=False)
    parent = models.ForeignKey("Message", verbose_name=_("Parent"), default=None, null=True, related_name="replies",blank=True)
    #order = models.PositiveIntegerField(verbose_name=_("order"),default=9999)
    last_update=models.DateTimeField(verbose_name=_("last update"), auto_now_add=True)

    def __unicode__(self):
        return "%s-%s-%s"%(self.author.username,self.course.name,self.published)

    
    def save(self, *args, **kwargs):
        if self.parent != None:
            self.parent.last_update = datetime.datetime.now();
            self.parent.save()
        self.last_update = datetime.datetime.now();
        super(Message, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = _("Mensaje")
        verbose_name_plural= _("Mensajes")
        ordering = ['-last_update']

    

'''
class CourseAccessRegistry(Base):
    user =  models.ForeignKey(User, verbose_name=_("Author"))
    course = course = models.ForeignKey(Course, verbose_name=_("Curso"))
    date = models.DateTimeField()

    class Meta:
        unique_together = ('user','course')
        verbose_name = _("Course Access Registry")
        verbose_name_plural= _("Course access registry")

    def __unicode__(self):
        return "%s-%s(%s)"%(self.user.username,self.course.code,self.date)
'''

'''
File : representa los ficheros asociados a un mensaje
'''
class File(Base):
    file = models.FileField(upload_to=content_file_name, verbose_name=_('Main Picture'), help_text=_("Select a picture to upload"))
    name = models.CharField(max_length=200, verbose_name=_("Nombre"))
    message = models.ForeignKey(Message,verbose_name=_("Mensaje"), related_name="message_files")
#  version = models.FloatField(verbose_name=_("Version"), default=1.0)
    type= models.CharField(choices=FILE_TYPES,verbose_name=("Tipo"), max_length=10, default=0)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _("Archivo")
        verbose_name_plural=_("Archivos")

    def delete(self, *args, **kwargs):
        self.file.delete()
        super(File,self).delete(*args,**kwargs)


'''
ResourceFile : Representa un fichero en la seccion "Recursos"
'''

class ResourceFile(Base):
    file = models.FileField(upload_to=resource_file_name, verbose_name=_('Archivo'), help_text=_("Elija un archivo para subir"),default= None, null=True, blank=True)
    name = models.CharField(max_length=200, verbose_name=_("Nombre"))
    description = models.TextField(max_length=200, verbose_name=_("Description"),blank=True, null=True)
    uploader = models.ForeignKey(User, verbose_name=_("Uploader"))
    
    def __unicode__(self):
        return "%s[%s]"%(self.name, self.uploader.username)

    class Meta:
        verbose_name = _("Archivo de recursos ")
        verbose_name_plural=_("Archivos de recursos")


    def delete(self, *args, **kwargs):
        self.file.delete()
        super(ResourceFile,self).delete(*args,**kwargs)


#@receiver(pre_delete)
#def file_delete(sender, instance, **kwargs):
#    list_of_models = ('File', 'ResourceFile')
#    if sender.__name__ in list_of_models:
#        instance.file.delete(False)

class Chapter(Base):
    order = models.IntegerField(verbose_name=_("Orden"), default=0)
    name = models.CharField(max_length=200, verbose_name=_("Nombre"))
    #body = models.TextField(verbose_name=_("Texto"))
    body = RichTextField()
    right = RichTextField(default="")
    parent = models.ForeignKey("Chapter", verbose_name=_("Capítulo Padre"), null=True, blank=True)
    theme = models.ForeignKey("Theme", verbose_name=_("Tema"))

    
    def __unicode__(self):
        return "%s"%(self.name)

    def get_order(self):
        if self.parent:
            return (self.parent.order, self.order)
        else:
            return (self.order, -1000)

    def childrens(self) :
        return Chapter.objects.filter(parent = self)

    class Meta:
        ordering = ["order"]
        verbose_name = _("Capítulo")
        verbose_name_plural=_("Capítulos")

class Theme(Base):
    order = models.IntegerField(verbose_name=_("Orden"), default=0)
    name = models.CharField(max_length=200, verbose_name=_("Nombre"))
    course = models.ForeignKey("Course", verbose_name=_("Curso"))
    
    def __unicode__(self):
        return "%s"%(self.name)

    @property
    def chapter_in_order(self):
        try:
            chapters = list(Chapter.objects.filter(theme=self))
            chapters = sorted(chapters, key=lambda x : x.get_order())
        except Exception as e:
            mylog(e)
        return chapters

    @property
    def chapter_root(self):
        chapters = Chapter.objects.filter(parent__isnull = True, theme=self)
        return chapters
    
    class Meta:
        ordering = ['order']
        verbose_name = _("Temas")
        verbose_name_plural=_("Temas")

