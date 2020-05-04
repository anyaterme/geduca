from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from web import views

urlpatterns = patterns('',
    url(r'^$', 'web.views.index', name='index'),
    url(r'^tag/create/$', 'web.views.create_tags', name='index'),

    url(r'^courses/list/$', 'web.views.courses_list', name="courses_list"),
    url(r'^course/details/(?P<course_id>\d+)/$','web.views.course_details',name="course_details"),
    
    #files
    url(r'^upload/', 'web.views.upload_files', name = 'jfu_upload' ),
    url(r'^delete/(?P<pk>\d+)', 'web.views.upload_delete', name='jfu_delete'),
    url(r'^files/upload/frame/(?P<message_id>\d+)/$','web.views.upload_frame', name='upload'),

    
    #messages
    url(r'^message/state/change/(?P<course_id>\d+)/(?P<message_id>\d+)/$','web.views.change_message_state',name='change_state'),
    url(r'^delete/message/$','web.views.delete_message', name="delete_message"),
    url(r'^edit/message/(?P<message_id>\d+)/$','web.views.edit_message', name="edit_message"),
    url(r'^delete/message/file/(?P<file_id>\d+)/$','web.views.delete_file', name='delete_file'),
    url(r'^reply/message/(?P<message_id>\d+)/$','web.views.reply_message', name='reply_message'),


    
    #resources
    url(r'^resources/list/$','web.views.resources_list', name="resources_list"),
    url(r'^resources/delete/(?P<resource_id>\d+)/$','web.views.resource_delete',name="resource_delete"),
    
    #users
    url(r'^user/profile/(?P<username>\w+)','web.views.view_profile', name="view_profile"),
    
    
    
    url(r'^staff/add/course/$','web.staff.add_course',name="add_course"),
    url(r'^staff/edit/course/(?P<course_id>\d+)/$','web.staff.edit_course',name="edit_course"),
    url(r'^staff/delete/course/$','web.staff.delete_course',name="delete_course"),
    url(r'^staff/add/user/$','web.staff.add_user',name="add_user"),
    url(r'^staff/users/list/$','web.staff.list_users',name="list_users"),
    url(r'^staff/edit/user/(?P<user_id>\d+)/$','web.staff.edit_user',name="edit_user"),
    url(r'^staff/delete/user/(?P<user_id>\d+)/$','web.staff.delete_user',name="delete_user"),
    url(r'^staff/disable/user/(?P<user_id>\d+)/$','web.staff.disable_user',name="disable_user"),
    url(r'^staff/restore/user/(?P<user_id>\d+)/$','web.staff.restore_user',name="restore_user"),

    url(r'^staff/add/category/$','web.staff.add_category',name="add_category"),
    url(r'^staff/add/user/course/(?P<course_id>\d+)/$','web.staff.user_course_add',name="user_course_add"),
    url(r'^staff/delete/user/course/(?P<user_id>\d+)/(?P<course_id>\d+)/$','web.staff.user_course_delete',name="user_course_delete"),
    # Temas
    url(r'^staff/add/theme/(?P<course_id>\d+)/$','web.staff.theme_course_manage',name="theme_course_manage"),
    url(r'^staff/add/theme/(?P<course_id>\d+)/(?P<theme_id>\d+)/$','web.staff.theme_course_manage',name="theme_course_manage"),
    url(r'^staff/save_theme/$','web.staff.save_theme',name="save_theme"),
    url(r'^staff/delete_theme/(?P<theme_id>\d+)/$','web.staff.delete_theme',name="delete_theme"),
    url(r'^staff/preview_theme/(?P<theme_id>\d+)/$','web.staff.preview_theme',name="preview_theme"),
    url(r'^staff/source_theme/(?P<theme_id>\d+)/$','web.staff.source_theme',name="source_theme"),
    url(r'^staff/new_source_theme/(?P<theme_id>\d+)/$','web.staff.new_source_theme',name="new_source_theme"),
    url(r'^staff/save_chapter/$','web.staff.save_chapter',name="save_chapter"),
    url(r'^staff/delete_chapter/(?P<chapter_id>\d+)/$','web.staff.delete_chapter',name="delete_chapter"),
    url(r'^staff/show_chapter_body/(?P<chapter_id>\d+)/$','web.staff.show_chapter_body',name="show_chapter_body"),
    url(r'^staff/save_chapter_body/$','web.staff.save_chapter_body',name="save_chapter_body"),
    url(r'^staff/chapter_up/(?P<chapter_id>\d+)/$','web.staff.chapter_up',name="chapter_up"),
    url(r'^staff/chapter_down/(?P<chapter_id>\d+)/$','web.staff.chapter_down',name="chapter_down"),
    url(r'^staff/chapter_left/(?P<chapter_id>\d+)/$','web.staff.chapter_left',name="chapter_left"),
    url(r'^staff/chapter_right/(?P<chapter_id>\d+)/$','web.staff.chapter_right',name="chapter_right"),
    url(r'^staff/download/(?P<theme_id>\d+)/(?P<theme_template>\w+)/$','web.staff.download',name="download"),
    url(r'^staff/theme_up/(?P<theme_id>\d+)/$','web.staff.theme_up',name="theme_up"),
    url(r'^staff/theme_down/(?P<theme_id>\d+)/$','web.staff.theme_down',name="theme_down"),
    url(r'^staff/fix/theme/order/$','web.staff.fix_theme_order',name="fix_theme_order"),

    url(r'^staff/clonecourse/(?P<fromcourse>\d+)/(?P<tocourse>\d+)/$', 'web.staff.clone_course', name='staff-clone-course'),
    url(r'^staff/clonecourse/(?P<tocourse>\d+)/$', 'web.staff.clone_course', name='staff-clone-course'),
    url(r'^staff/clonecourse/$', 'web.staff.clone_course', name='staff-clone-course'),
    url(r'^staff/test/$', 'web.staff.test', name='staff-test'),
    url(r'^staff/fix-chapter-parents/(?P<theme_id>\d+)/$', 'web.staff.fix_chapter_parents', name='fix_chapter_parents'),



    #url(r'^staff/browse/(?P<chapter_id>\d+)/$','web.staff.browse',name="browse"),
    #url(r'^staff/upload/$','web.staff.upload',name="upload"),
)
