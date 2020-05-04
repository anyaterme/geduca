from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import get_template, render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import random, string, os, datetime


def web_send_mail(template_path, context, subject, from_email ,to):
	html_content = render_to_string(template_path,context)
	text_content = strip_tags(html_content)
	msg = EmailMultiAlternatives(subject, text_content, from_email,to)
	msg.attach_alternative(html_content, "text/html")
	print msg.send()

def get_element (model,pk):
	response = {}
	try :
		response = model.objects.get(pk=int(pk))
	except ObjectDoesNotExist:
		response = False;

	return response 

def random_str(length=8):
   letters = string.ascii_uppercase
   return ''.join(random.choice(letters) for i in range(length))


def mylog(message):
    logfile = open(os.path.join(settings.PROJECT_ROOT,"debug.log"), "a", 0)
    message = str(message)
    logfile.write("%s:> %s\n" % (datetime.datetime.now(), message))
    logfile.close()
