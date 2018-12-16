# -*- encoding: utf-8 -*-
import userena
import os 
import sys
from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.sites.models import Site
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.paginator import Paginator, InvalidPage
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, render_to_response, redirect
from django.template import Context
from django.template.loader import get_template, render_to_string
from django.utils.html import strip_tags
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST
from accounts.models import Profile

from jfu.http import upload_receive, UploadResponse, JFUResponse


from web.models import *
from web.utils import *
from web.forms import *


def send_message_email(request,message):
	pass	
	#users = User.objects.filter(user_course__course=message.course)
	#email_list=[]
	#for item in users:
	#	if len(item.email) > 3:
	#		email_list.append(item.email)
	#email_context = {'message': message,'request':request, 'site':Site.objects.get_current()}
	#subject = "GEDUCA: Nuevo mensaje en %s"%(message.course.name)
	#web_send_mail('message_email.html',email_context,subject,'no-reply',email_list)

def index (request):

	if request.user.is_authenticated() :
		return redirect(courses_list)
	else:
		return redirect(userena.views.signin);


def dashboard (request):
	
	return render(request,'dashboard.html',{})
	pass



def courses_list (request):

	if request.user.is_authenticated():
		context ={}
		if request.user.is_superuser:
			courses  = Course.objects.all().order_by('-creation_date')
		else:
			courses = Course.objects.filter(course_user__user=request.user).order_by('-creation_date')
		if len(courses) < 1 :
			context['empty'] = True

		if request.method == 'POST':
			search_str  = request.POST.get('search_str',False)
			if search_str != False :
				search_str = search_str.strip()
				if len (search_str) > 1:
					search_str = remove_accents(search_str)
					courses = courses.filter(tag__name__icontains=search_str)
					#query_str = "unaccent(lower(name)) LIKE %s OR lower(name) LIKE %s OR lower(code) LIKE %s"
					#search_str = "%"+search_str+"%"
					#search_str = search_str.lower()
					#print search_str
					#courses = courses.extra(where=[query_str] , params=[search_str,search_str,search_str])
			category_id = request.POST.get('search_param',False)
			if category_id != False and category_id != '-1':
				courses = courses.filter(category__id=int(category_id))
			
		context['courses']=courses
		context['categories'] = Category.objects.all()
		context['lapse'] = LAPSE 
		return render (request,'courses_list.html',context)
	else:
		return redirect(userena.views.signin)

def edit_message(request, message_id):
	if request.user.is_authenticated():
		context = {}
		message = get_element(Message, message_id)
		if message != False and message.author == request.user:
			context['course'] = message.course
			
			form = MessageForm(instance=message)
			context['files'] = File.objects.filter(message=message)
			if request.method == "POST":
				form = MessageForm(request.POST,instance=message)
				if form.is_valid():
					if len(form.cleaned_data['content']) < 1:
						message.content = "(Sin contenido)"
					else:
						message.content = form.cleaned_data['content']

					if len (form.cleaned_data['subject'])< 1 :
						message.subject = _("(Sin Asunto)")
					else:
						message.subject = form.cleaned_data['subject']
					message.priority = form.cleaned_data['priority']
					message.save()
					#send_message_email(request,message)
					return redirect(course_details, course_id=message.course.id)
				else: 
					sys.stderr.write("FORMULARIO NO VALIDO.\n")

			context['form_message']= message;
			context['form'] = form

		else:
			context['error'] = _(" No tiene permisos para modificar este mensaje")
			context['form_message'] = message
	
		return render(request,"edit_message.html",context)

	else:
		return redirect(index)


def reply_message(request,message_id):
	context={}
	if request.user.is_authenticated():
		parent = get_element(Message,message_id)
		if parent != False:
			course = parent.course
			try :
				form_message = Message.objects.get(author=request.user,course=course,published=False,parent=parent)
				
			except ObjectDoesNotExist:
				form_message = Message.objects.create (
					author = request.user,
					course = course,
					parent = parent,
					subject= "",
					content= "",
					published = False)
			else:
				if request.method != "POST":
					#FIXME: es posible que el mensaje no se publicara y se subieran archivos por lo que los eliminamos 
					file_messages = File.objects.filter(message=form_message)
			 		for item in file_messages:
						item.delete()

			context['parent'] = parent
			form = MessageForm()
			if request.method == "POST":
				form = MessageForm(request.POST)
				if form.is_valid():
					if len(form.cleaned_data['content']) < 1:
						form_message.content = "(Sin contenido)"
					else:
						form_message.content = form.cleaned_data['content']

					if len (form.cleaned_data['subject'])< 1 :
						form_message.subject = _("(Sin Asunto)")
					else:
						form_message.subject = form.cleaned_data['subject']
					form_message.author = request.user
					form_message.course = course
					form_message.parent = parent
					form_message.priority = form.cleaned_data['priority']
					form_message.published=True
					form_message.save()
					send_message_email(request,form_message)
					return redirect(course_details, course_id=course.id)
				else: 
					print "ERROR EN EL FORMULARIO"

			context['form'] = form
			context['form_message']= form_message
			context['course'] = course
		else:
			context['error'] =_("Parent not found")
	else:
		return redirect(index)

	return render(request,"reply_message.html",context)

def course_details(request,course_id):
	
	if request.user.is_authenticated():
		course = get_element(Course,course_id)

		form = MessageForm
		f_form = FileForm
		
		if course != False:
			try: 
				last_access = CourseUser.objects.get(course=course, user=request.user) 
			except ObjectDoesNotExist:
				last_access = CourseUser.objects.create(
					course=course,
					user=request.user,
					date= datetime.datetime.now(),
				)
			else:
				last_access.date = datetime.datetime.now()
				last_access.save()

			try :
				form_message = Message.objects.get(author=request.user,course=course,published=False,parent=None)
				
			except ObjectDoesNotExist:
				form_message = Message.objects.create (
					author = request.user,
					course = course,
					subject= "",
					content= "",
					published = False)
			else:
				if request.method != "POST":
					#FIXME: es posible que el mensaje no se publicara y se subieran archivos por lo que los eliminamos 
					file_messages = File.objects.filter(message=form_message)
			 		for item in file_messages:
						item.delete()


			files = File.objects.filter(message__course=course, message__published=True).order_by('-creation_date')
			users_course = CourseUser.objects.filter(course=course)
			messages = Message.objects.filter(course=course,published=True,parent=None).order_by('-last_update')
			if request.method == "POST":
				form = MessageForm(request.POST)
				if form.is_valid():
					if len(form.cleaned_data['content']) < 1:
						form_message.content = "(Sin contenido)"
					else:
						form_message.content = form.cleaned_data['content']

					if len (form.cleaned_data['subject'])< 1 :
						form_message.subject = _("(Sin Asunto)")
					else:
						form_message.subject = form.cleaned_data['subject']
					form_message.author = request.user
					form_message.course = course
					form_message.priority = form.cleaned_data['priority']
					form_message.published=True
					form_message.save()
					send_message_email(request,form_message)
					form = MessageForm()
					form_message = Message.objects.create (
						author = request.user,
						course = course,
						subject= "",
						content= "",
						published = False)
					return redirect(course_details, course_id=course_id)
				else: 
					print "ERROR EN EL FORMULARIO"


			context = {
				'course': course,
				'files' : files,
				'form_message': form_message,
				'users_course' : users_course,
				'MESSAGE_STATES':MESSAGE_STATES,
				'messages' : messages,
				'form' : form,
				'f_form': f_form,
			}
			return render(request,'course_details.html',context)
		else:
			return HttpResponse("Course NOT FOUND SCREEN")
	
	return HttpResponse("FORBIDDEN_SCREEN")


'''
def course_details(request,course_id):
	
	if request.user.is_authenticated():
		course = get_element(Course,course_id)

		form = MessageForm
		f_form = FileForm
		
		if course != False:
			try: 
				last_access = CourseUser.objects.get(course=course, user=request.user) 
			except ObjectDoesNotExist:
				last_access = CourseUser.objects.create(
					course=course,
					user=request.user,
					date= datetime.datetime.now(),
				)
			else:
				last_access.date = datetime.datetime.now()
				last_access.save()

			try :
				form_message = Message.objects.get(author=request.user,course=course,published=False)
				
			except ObjectDoesNotExist:
				form_message = Message.objects.create (
					author = request.user,
					course = course,
					subject= "",
					content= "",
					published = False)
			else:
				if request.method != "POST":
					#FIXME: es posible que el mensaje no se publicara y se subieran archivos por lo que los eliminamos 
					file_messages = File.objects.filter(message=form_message)
			 		for item in file_messages:
						pass
						#item.delete()


			files = File.objects.filter(message__course=course, message__published=True).order_by('-creation_date')
			users_course = CourseUser.objects.filter(course=course)
			messages = Message.objects.filter(course=course,published=True).order_by('-creation_date')
			if request.method == "POST":
				form = MessageForm(request.POST)
				if form.is_valid():
					if len(form.cleaned_data['content']) < 1:
						form_message.content = "(Sin contenido)"
					else:
						form_message.content = form.cleaned_data['content']

					if len (form.cleaned_data['subject'])< 1 :
						form_message.subject = _("(Sin Asunto)")
					else:
						form_message.subject = form.cleaned_data['subject']
					form_message.author = request.user
					form_message.course = course
					form_message.priority = form.cleaned_data['priority']
					form_message.published=True
					form_message.save()
					form = MessageForm()
					form_message = Message.objects.create (
						author = request.user,
						course = course,
						subject= "",
						content= "",
						published = False)
					send_message_email(request,form_message)
					return redirect(course_details, course_id=course_id)
				else: 
					print "ERROR EN EL FORMULARIO"


			context = {
				'course': course,
				'files' : files,
				'form_message': form_message,
				'users_course' : users_course,
				'MESSAGE_STATES':MESSAGE_STATES,
				'messages' : messages,
				'form' : form,
				'f_form': f_form,
			}
			return render(request,'course_details.html',context)
		else:
			return HttpResponse("Course NOT FOUND SCREEN")
	
	return HttpResponse("FORBIDDEN_SCREEN")

'''


def change_message_state(request,course_id,message_id):
	if request.user.is_authenticated() and request.user.is_staff:
		message = get_element(Message,message_id)
		new_status = request.GET.get('status',False)
		if message != False and new_status != False:
			message.status = new_status
			message.save()

	return redirect(course_details, course_id=course_id)

			


def delete_message(request):
	if request.user.is_authenticated():
		message_id = request.GET.get('message',False)
		if message_id != False:
			message = get_element(Message,message_id)
			if message != False:
				if request.user == message.author or request.user.is_superuser:
					course_id = message.course.id
					message.delete()
				else:
					sys.stderr.write("--- User has no permits to delete this message----\n")


			return redirect(course_details, course_id=course_id)
			

	
def delete_file(request,file_id):
	sys.stderr.write("delete file\n")

	response = {
		'status': False,
		'error': False,
		'error_msg' : False,
	}

	if request.user.is_authenticated():
		sys.stderr.write(" user authenticated\n")

		file_obj = get_element(File,file_id)
		if file_obj != False:
			course_id = file_obj.message.course.id;
			if request.user == file_obj.message.author or request.user.is_superuser:
				file_obj.delete()
				response['status'] = True
			else:
				sys.stderr.write(" user has no permits to delete this file\n")
				response ['error'] = True
				response ['error_msg'] = _("User %s has no permits to delete this file "%(request.user.username))
		else:
			sys.stderr.write("---File not found ----1\n")
			response ['error'] = True
			response ['error_msg'] = _("File not found")
		
	
	return HttpResponse(json.dumps(response), mimetype="application/json")


@require_POST
def upload_files(request):
	
	# The assumption here is that jQuery File Upload
   # has been configured to send files one at a time.
   # If multiple files can be uploaded simulatenously,
	if not request.user.is_authenticated():
		Uploadresponse(request, {})

	message_id = request.POST.get('message','-1')
	message = get_element(Message,int(message_id))
	if message == False:
		return UploadResponse(request, {})
	
	file = upload_receive( request )
  	instance = File( file=file, name= file.name, message=message )
  	instance.save()
	basename = os.path.basename( instance.file.path )
 	file_dict = {
	  'name' : basename,
	  'size' : file.size,
	  'url': settings.MEDIA_URL + basename,
	  'thumbnailUrl': settings.MEDIA_URL + basename,
	  'delete_url': reverse('jfu_delete', kwargs = { 'pk': instance.pk }),
	  'delete_type': 'POST',
	}

	return UploadResponse( request, file_dict )


@require_POST
def upload_delete( request, pk ):
	success = True
	try:
		instance = File.objects.get( pk = pk )
		os.unlink( instance.file.path )
		instance.delete()
	except File.DoesNotExist:
		success = False
		
	return JFUResponse( request, success )	

def upload_frame(request,message_id):
	return render(request,"upload.html",{ 'message_id':message_id })


def view_profile(request,username):
	if request.user.is_authenticated(): 
		try :
			user = User.objects.get(username=username)
		except ObjectDoesNotExist:
			user = False
		
		return render(request,'userena/profile_detail.html',{'user':user})
	return HttpResponse("403 Forbidden")


def resources_list (request):
	if request.user.is_authenticated():
		context = { 'resources' : ResourceFile.objects.filter(uploader=request.user).order_by('-creation_date') }

		form = ResourceFileForm()
		if request.method == 'POST':
			form = ResourceFileForm(request.POST, request.FILES,initial={'uploader': request.user })
			if form.is_valid():
				resource_file = form.save()
				return redirect(resources_list)

		context['form'] = form


		return render(request,'resources_list.html',context)
	return HttpResponse("403 Forbidden")
		


def resource_delete(request, resource_id):
	
	if request.user.is_authenticated(): 
		resource = get_element(ResourceFile,resource_id)
		if resource != False:
			if resource.uploader == request.user or request.user.is_superuser:
				resource.delete()
				return redirect(resources_list)
			
	
	return HttpResponse("403 Forbidden")


def create_tags(request):
	courses = Course.objects.all()
	for course in courses :
		course.save()
	
	profiles = Profile.objects.all()
	for profile in profiles:
		profile.save()

	return HttpResponse("Generated")

	
	
