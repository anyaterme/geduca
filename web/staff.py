# -*- encoding: utf-8 -*-
import userena
import os 
import re
from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.paginator import Paginator, InvalidPage
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Max,Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, render_to_response, redirect
from django.template import Context
from django.template.loader import get_template, render_to_string
from django.utils.html import strip_tags
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST
from web import views

import zipfile
import StringIO

from staff_forms import *

from web.views import courses_list, course_details 
from web.utils import *

def add_course(request):
	
	if request.user.is_authenticated() and request.user.is_staff:
		context = {}
		context['title'] = _("Nuevo Curso")
		context['form'] = CourseForm()
		if request.method == 'POST':
			form =CourseForm(request.POST)
			if form.is_valid():
				course = form.save()
				return redirect(course_details, course.id)
			context['form']  = form

		return render(request,"course_form.html",context)
	else:
		return redirect(views.index)

def edit_course(request,course_id):
	if request.user.is_authenticated() and request.user.is_staff:
		course = get_element(Course,course_id)
		if course != False:
			context={}
			context['title'] = _("Modificar Curso")
			form = CourseForm(instance=course);
			if request.method == 'POST':
				form = CourseForm(request.POST, instance=course)
				if form.is_valid():
					course = form.save();
					return redirect(course_details, course_id)
			context['form'] = form
		return render(request,"course_form.html",context)
	else:
		return redirect(views.index)

def delete_course(request):
	if request.user.is_authenticated and request.user.is_staff:
		course_id = request.GET.get('course',False)
		if course_id  != False:
			course = get_element(Course,course_id)
			if course != False:
				course.delete()
				return redirect(courses_list)
		
		
	return redirect(views.index)

def add_category(request):

	if request.user.is_authenticated and request.user.is_staff:
		context = {'form': CategoryForm()}
		if request.method == 'POST':
			form = CategoryForm(request.POST)
			if form.is_valid():
				category = form.save()
				return redirect(courses_list)
			else: 
				context['form'] = form 
		return render(request,"category_form.html",context)
	
	return redirect(views.index)



def list_users(request):

	if request.user.is_authenticated and request.user.is_staff:	
		users = User.objects.filter(is_superuser=False ,pk__gt=1)
		if request.method == 'POST':
			search_str  = request.POST.get('search_str',False)
			if search_str != False :
				search_str = search_str.strip()
				if len (search_str) > 1:
                                        search_str = remove_accents(search_str)
					users = users.filter(profile__tag__name__icontains=search_str)
					#query_str = " unaccent(lower(first_name)) LIKE %s OR lower(first_name) LIKE %s OR lower(last_name) LIKE %s " 
					#query_str += " OR unaccent(lower(last_name)) LIKE %s OR lower(email) LIKE %s OR (lower(first_name) || lower(last_name)) LIKE %s" 
					#query_str += " OR unaccent(lower(first_name) || lower(last_name)) LIKE %s OR unaccent(lower(first_name)) || lower(last_name) LIKE %s"
					#query_str += " OR lower(first_name) || unaccent(lower(last_name)) LIKE %s "
					#search_str =search_str.replace(" ","%").lower()
					#search_str = "%"+search_str+"%"
					#users = users.extra(where=[query_str] , params=[search_str,search_str,search_str,search_str,search_str,search_str,search_str, search_str, search_str])
		if request.user.is_superuser :
			users = users.filter(~Q(pk=request.user.id))
		context = {'users': users}
		return render(request,"users_list.html",context)
	
	return redirect(views.index)
	


@transaction.commit_manually
def add_user(request):
	if request.user.is_authenticated and request.user.is_staff:
		try:
			context = {'form':UserForm() ,'profile_form':ProfileForm()}
			context['title'] = _("Crear Usuario")
			if request.method == 'POST':
				form = UserForm(request.POST)
				profile_form=ProfileForm(request.POST)
				if form.is_valid():
					user_with_email = User.objects.filter(email = form.cleaned_data['email']);
					if len(user_with_email) < 1:
						user = form.save(commit=False)
						user.set_password(form.cleaned_data['password'])
						profile_fields = request.POST.copy()
						user.save()
						#sid = transaction.savepoint_commit()
						profile_fields['user'] = user.id
						profile_fields['privacy'] = "registered"
						profile_form =ProfileForm(profile_fields)
						if profile_form.is_valid():
							profile = profile_form.save(commit=False)
							profile.save()
							transaction.commit()
							return redirect(list_users)
						else :
							print profile_form.errors
							transaction.rollback()
					else:
						context['error'] = _(" Ya existe un usuario con esa direccion de email")

				context['form'] = form 
				context['profile_form']=profile_form
			transaction.rollback()	
			return render(request,'user_form.html',context)
		finally:
			transaction.rollback()
	
	return redirect(views.index)

def edit_user(request, user_id):
	context = {}
	context['title'] = _("Modificar Usuario")
	context['edit'] = True
	if request.user.is_authenticated and request.user.is_staff:
		edit_user = get_element(User,user_id)
		try: 
			profile = edit_user.profile
		except ObjectDoesNotExist:
			profile = Profile.objects.create(user=edit_user)
		if not edit_user.is_superuser:
			context['form'] = UserForm(instance=edit_user)
			context['profile_form'] = ProfileForm(instance=profile)
			if request.method == 'POST':
				form = UserForm(request.POST, instance=edit_user)
				profile_fields = request.POST.copy()
				profile_fields['user'] = profile.user.id
				profile_fields['privacy'] = 'registered'
				profile_form = ProfileForm(profile_fields, instance=profile)
				if form.is_valid() and profile_form.is_valid():
					user_with_email = User.objects.filter(email = form.cleaned_data['email']);
					if len(user_with_email) <= 1:
						edit_user = form.save()
						edit_user.set_password(form.cleaned_data['password'])
						edit_user.save()
						profile = profile_form.save()
						profile.save()
						return redirect(list_users)
					else:
						context['error'] = _(" Ya existe un usuario con esa dirección de email ")

				context['form'] = form
				context['profile_form'] = profile_form;
			return render(request,'user_form.html',context)

	return redirect(views.index)
		

def disable_user(request, user_id):
	#el staff solo puede desactivar usuarios para que no se eliminen mensajes y archivos
	if request.user.is_authenticated and request.user.is_staff:
		del_user = get_element(User,user_id)
		if not del_user.is_superuser:
			del_user.is_active = False
			del_user.save()
			return redirect(list_users)
	
	return redirect(views.index)

def delete_user(request, user_id):
	if request.user.is_authenticated and request.user.is_superuser:
		drop_user = get_element(User, user_id)
		drop_user.delete();

		return redirect(list_users)

	return redirect(views.index)



def restore_user(request,user_id):
	if request.user.is_authenticated and request.user.is_staff:
		user  = get_element(User,user_id)
		user.is_active = True
		user.save()
		return redirect(list_users)
	
	return redirect(views.index)


def user_course_add(request,course_id):
	if request.user.is_authenticated  and request.user.is_staff:
		context={ 'form':CourseUserForm(initial={'course':course_id}) }
		if request.method == 'POST':
			form = CourseUserForm(request.POST,initial={'course':course_id})
			if form.is_valid():
				course_user = form.save()
				return redirect(course_details,course_id=course_id)
			context['form'] = form
		context['course_id'] = course_id
		return render(request,'course_user.html',context)

	return redirect(views.index)
		


def user_course_delete(request,user_id,course_id):
	if request.user.is_authenticated and request.user.is_staff:
		user = get_element(User,user_id)
		course = get_element(Course,course_id)
		if user != False and course != False :
			if not user.is_superuser or request.user.is_superuser:
				try :
					user_course = CourseUser.objects.get(user=user,course=course)
				except ObjectDoesNotExist:
					pass
				else:
					user_course.delete()
					

	return redirect(views.index)

'''
    Theme area
'''
def theme_course_manage(request, course_id, theme_id=None):
    if request.user.is_authenticated and request.user.is_staff:
        course = Course.objects.get(pk=course_id)
        theme = None if theme_id == None else Theme.objects.get(pk=theme_id)
        #if request.method == 'POST':
        #    theme = Theme(name=request.POST["name"], course=course)
        #    theme.save()
        context = {'course': course, 'theme': theme}
        return render(request, 'course_theme.html', context)
    return redirect(views.index)

def save_theme(request):
    course = Course.objects.get(pk=request.POST["course_id"])
    if "theme_id" not in request.POST:
		 order = Theme.objects.all().aggregate(Max('order'))['order__max']
		 order = 0 if order == None else (order + 1)
		 theme = Theme(name=request.POST["name"], course=course, order=order)
		 theme.save()
    else:
       theme = Theme.objects.get(pk=request.POST["theme_id"])
       theme.name = request.POST["name"]
       theme.save()
    context = {'course': course, 'theme': theme}
    return render(request, 'course_theme.html', context)
    #return render(request, 'theme_name.html', context)

def preview_theme(request, theme_id):
    theme = Theme.objects.get(pk=theme_id)
    context = {'course': theme.course, 'theme': theme}
    return render(request, 'theme_template.html', context)

def source_theme(request, theme_id):
    theme = Theme.objects.get(pk=theme_id)
    context = {'course': theme.course, 'theme': theme}
    return render(request, 'theme_template_source.html', context)

def new_source_theme(request, theme_id):
    theme = Theme.objects.get(pk=theme_id)
    context = {'course': theme.course, 'theme': theme}
    return render(request, 'theme_template_source_new.html', context)

def delete_theme(request, theme_id):
    theme = Theme.objects.get(pk=theme_id)
    for chapter in theme.chapter_set.all():
        chapter.delete()
    theme.delete()
    context = {'course': theme.course,'theme': theme}
    return render(request, 'theme_panel.html', context)

def save_chapter(request):
    theme = Theme.objects.get(pk=request.POST["theme_id"])
    if "chapter_id" not in request.POST:
        order = Chapter.objects.all().aggregate(Max('order'))['order__max']
        order = 0 if order == None else (order + 1)
        chapter = Chapter(name=request.POST["name"], theme=theme, order=order)
        chapter.save()
    else:
       chapter = Chapter.objects.get(pk=request.POST["chapter_id"])
       chapter.name = request.POST["name"]
       chapter.save()
    context = {'theme': theme}
    return render(request, 'theme_chapters.html', context)

def delete_chapter(request, chapter_id):
    chapter = Chapter.objects.get(pk=chapter_id)
    theme = chapter.theme
    chapter.delete()
    context = {'theme': theme}
    return render(request, 'theme_chapters.html', context)

def chapter_up(request, chapter_id):
    chapter = Chapter.objects.get(pk=chapter_id)
    order = chapter.order
    if chapter.order > 0:
        previous_chapter = Chapter.objects.filter(order=(order - 1))[0]
        chapter.order = order - 1
        chapter.save()
        previous_chapter.order = order
        previous_chapter.save()
    context = {'theme': chapter.theme}
    return render(request, 'theme_chapters.html', context)


def chapter_down(request, chapter_id):
    chapter = Chapter.objects.get(pk=chapter_id)
    order = chapter.order
    max_order = Chapter.objects.all().aggregate(Max('order'))['order__max']
    if chapter.order < max_order:
        next_chapter = Chapter.objects.filter(order=(order + 1))[0]
        chapter.order = order + 1
        chapter.save()
        next_chapter.order = order
        next_chapter.save()
    context = {'theme': chapter.theme}
    return render(request, 'theme_chapters.html', context)

def chapter_left(request, chapter_id):
    chapter = Chapter.objects.get(pk=chapter_id)
    if chapter.parent != None:
        chapter.parent = None
        chapter.save()
    context = {'theme': chapter.theme}
    return render(request, 'theme_chapters.html', context)

def chapter_right(request, chapter_id):
    chapter = Chapter.objects.get(pk=chapter_id)
    order = chapter.order
    if chapter.order > 0:
        previous_chapter = Chapter.objects.filter(order=(order - 1))[0]
        chapter.parent = previous_chapter
        chapter.save()
    context = {'theme': chapter.theme}
    return render(request, 'theme_chapters.html', context)


def fix_theme_order (request):
	themes = Theme.objects.all()
	counter = 0;
	for item in themes :
		item.order = counter;
		item.save()
		counter = counter +1 ;
	return HttpResponse(" <h2> orden preestablecido </h2>")



def theme_up(request, theme_id):
	theme = get_element(Theme,theme_id)	
	order = theme.order
	if theme.order > 0:
		previous_theme = Theme.objects.filter(order=(order - 1))[0]
		theme.order = order - 1
		theme.save()
		previous_theme.order = order
		previous_theme.save()
	return redirect(views.course_details,theme.course.id)


def theme_down(request, theme_id):
	theme = get_element(Theme,theme_id)
	order = theme.order
	max_order = Theme.objects.all().aggregate(Max('order'))['order__max']
	if theme.order < max_order:
		next_theme = Theme.objects.filter(order=(order + 1))[0]
		theme.order = order + 1
		theme.save()
		next_theme.order = order
		next_theme.save()
	return redirect(views.course_details,theme.course.id)


def show_chapter_body(request, chapter_id):
	chapter = Chapter.objects.get(pk=chapter_id)
	form = ChapterForm(instance=chapter)
	context = {'chapter': chapter, 'myform': form}
	return render(request, 'chapter_body.html', context)

def save_chapter_body(request):
	chapter = Chapter.objects.get(pk=request.POST["chapter_id"])
	chapter.body = request.POST["body"]
	chapter.right = request.POST["right"]
	chapter.save()
	form = ChapterForm(instance=chapter)
	context = {'chapter': chapter, 'myform': form}
	return render(request, 'chapter_body.html', context)

def download(request, theme_id, theme_template):
	theme = Theme.objects.get(pk=theme_id)
	theme_path = MEDIA_ROOT+'/html_themes/theme.html'
	#Recopilamos los ficheros necesarios para el .zip
	filenames = get_theme_files(theme, theme_path, theme_template)

	#Creamos la estructuta del .zip
	zip_subdir = "themefiles"
	zip_filename = "%s.zip" % zip_subdir
	s = StringIO.StringIO()
	zf = zipfile.ZipFile(s, "w")

	#agregamos los ficheros al .zip
	zf = add_to_zip(zf, filenames, zip_subdir, theme_path)

	# Grab ZIP file from in-memory, make response with correct MIME-type
	resp = HttpResponse(s.getvalue(), mimetype = "application/x-zip-compressed")
	# ..and correct content-disposition
	resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

	return resp

def get_theme_files(theme, theme_path, theme_template):
	#Generamos un string con el html del tema
	context = {'course': theme.course, 'theme': theme}
	theme_str = render_to_string(theme_template+".html", context)

	test = 'img src="1234"'
	m = re.findall('src="/media/(.+?)"', theme_str)
	#Extraemos las imagenes a una lista y añadimos el fichero html con el tema
	page_files = [MEDIA_ROOT+"/"+image for image in m]

	#Reemplazamos la ruta a las imagenes para que funciones en el directorio comprimido
	for img in m:
		theme_str = theme_str.replace("/media/"+img, "./imgs/" + os.path.basename(img))

	#sb = re.findall('src="(.+?/sanborondon/.+?)"', theme_str)
	#for img in sb:
	#	print img

	#Creamos el fichero con el html del tema 
	theme_str = replace_charset(theme_str)
	theme_file = open(theme_path, 'w')
	theme_file.write(theme_str)
	theme_file.close()

	return page_files

def replace_charset(theme_str):
	theme_str = theme_str.replace("á","&aacute;").replace("é","&eacute;").replace("í","&iacute;").replace("ó","&oacute;").replace("ú","&uacute;")
	#theme_str = theme_str.replace("¿","&iquest;").replace("¡","&iexcl;")

	return theme_str

def add_to_zip(zf, filenames, zip_subdir, theme_path):
	#Guardamos las imagenes en una carpeta imgs
	for fpath in filenames:
		# Calculate path for file in zip
		fdir, fname = os.path.split(fpath)
		zip_path = os.path.join(zip_subdir+"/imgs", fname)
		# Add file, at correct path
		zf.write(fpath, './'+zip_path)

	#Guardamos el fichero html en la raiz
	fdir, fname = os.path.split(theme_path)
	zip_path = os.path.join(zip_subdir, fname)
	zf.write(theme_path, './'+zip_path)

	# Must close zip for all contents to be written
	zf.close()
	return zf
