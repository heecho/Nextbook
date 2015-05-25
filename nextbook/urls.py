from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
	url(r'^$', 'accounts.views.main', name='main'),
	url(r'^about$', 'accounts.views.about', name='about'),
	url(r'^recommendations$', 'groups.views.my_rec', name='myrec'),
    url(r'^admin/', include(admin.site.urls)),
	url(r'^group/', include('groups.urls', namespace = 'groups')),
	url(r'^members/', include('accounts.urls', namespace = 'members'))  
]