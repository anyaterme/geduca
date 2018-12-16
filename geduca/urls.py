from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'geduca.views.home', name='home'),
    # url(r'^geduca/', include('geduca.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
	 url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
	 url(r'^i18n/', include('django.conf.urls.i18n')),
	 url(r'^ckeditor/', include('ckeditor.urls')),
)

urlpatterns += i18n_patterns('',
    url(r'^', include('web.urls')),
	 url(r'^accounts/', include('userena.urls')),
	 url(r'^tinymce/', include('tinymce.urls')),
)
