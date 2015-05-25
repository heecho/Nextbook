from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [

    #url(r'^new$', 'groups.views.create_group', name = 'newgroup'),
    url(r'^(?P<group_id>[0-9]+)/?$','groups.views.home', name = 'home'),
    url(r'^(?P<group_id>[0-9]+)/recommendations/create','groups.views.run_rec', name = 'runrec'),
	url(r'^(?P<group_id>[0-9]+)/recommendations/(?P<rec_id>[0-9]+)?$','groups.views.show_rec', name = 'showrec'),   
    #url(r'^(?P<group_id>[0-9]+)/recommendations','groups.views.my_rec', name = 'myrec'),
    #url(r'^(?P<group_id>[0-9]+)/recommendations/enter?$','groups.views.enter_rec', name = 'enterrec'),
    
    
]