from django.conf.urls import include, url
from django.contrib import admin

from . import views

urlpatterns = [
    # Examples:
    # url(r'^$', 'nextbook.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', views.home, name = 'home'),
    url(r'^signup$', views.signup, name = 'signup'),
    url(r'^register$', views.register, name='create'),
    url(r'^signin$', views.signin, name = 'signin'),
    url(r'^login_user$', views.login_user, name='login_user'),
    url(r'^logout/', views.log_out, name = 'logout')
]