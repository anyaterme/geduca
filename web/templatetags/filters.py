# -*- encoding: utf-8 -*-

import datetime
import os;
import sys
from django import template
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _,  to_locale, get_language, ugettext as ugt
from django.db.models import Count
from web.models import *

register= template.Library();

@register.filter
def get_unread_messages(course,user):
	
	try:
		last_visit = CourseUser.objects.get(course=course,user=user)
	except ObjectDoesNotExist:
		messages = Message.objects.filter(course=course,published=True)
	else:
		last_visit = last_visit.date
		messages = Message.objects.filter(course=course,creation_date__gt=last_visit,published=True)

	return len(messages)


@register.filter
def is_empty(ls):
	if len(ls) < 1:
		return True
	return False

@register.filter
def file_size(file_obj):
	size = "";
	try:
		size = file_obj.file.size
	except:
		size ="--Mb"
	else:
		size = float(size / 1024)
		size = float(size/1024)
		size = "%.2fMb"%(size)

	return size


@register.filter
def course_finished(course):
	if int(course.status) < 2 :
		return False
	return True

@register.filter
def get_course_status(status):
	if status=='0':
		return '<span class="label label-default">Desarrollo</span>'
	elif status =='1':
		return '<span class="label label-warning">Producci&oacute;n</span>'
	elif status == '2':
		return '<span class="label label-success">Terminado</span>'
	else: 
		return ""

@register.filter
def get_message_status(status):
	if status == '0':
		return '<span class="label label-default">Abierto</span>'
	elif status == '1':
		return '<span class="label label-primary">Trabajando</span>'
	elif status =='2':
		return '<span class="label label-success">Resuelto</span>'
	elif status =='3':
		return '<span class="label label-danger">Error</span>'

	else:
		return ""

@register.filter
def get_message_priority(priority):
	if priority == '0':
		return '<span class="label label-default">Normal</span>'
	elif priority == '1':
		return '<span class="label label-warning">Importante</span>'
	elif priority =='2':
		return '<span class="label label-danger">Urgente</span>'

@register.filter
def get_role_name (role):
	if role :
		for item in ROL:
			if item[0] == role :
				return item[1]
	else:
		return "Admin"


@register.filter
def can_edit_message (user,message):
	if user == message.author or user.is_superuser:
		return True
	return False
