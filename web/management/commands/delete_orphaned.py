import os
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from web.models import *

def delete_files(path, delete = False):
	file_list = os.listdir(path)
	for f in file_list:
		new_path = os.path.join(path, f)
		if (os.path.isdir(new_path)):
			print "Entrando en directorio %s" % (f)
			delete_files(new_path, delete)
		else:
			db_file = File.objects.filter(file__contains=f)
			if len(db_file) == 0: 
				print "\t Removing %s..." % (f)
				if delete:
					os.remove(new_path)

class Command(BaseCommand):
	help = 'Delete orphaned...'

	def handle(self, *args, **options):
		path = os.path.join(settings.MEDIA_ROOT, 'media')
		path = os.path.join(path, 'courses')
		if "delete" in args:
			delete_files(path, True)
		else:
			delete_files(path)

