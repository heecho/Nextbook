from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from accounts.models import GRData
from groups.models import Book, Group, Recommendation
from accounts import goodreads
from django.contrib.auth import authenticate, login, logout
# Create your views here.

def main(request):
	user = request.user
	return render(request,'accounts/main.html',{'user':user})

def about(request):
	return render(request,'accounts/about.html',{})

def home(request):
	user = request.user
	groups = user.group_set.all()
	return render(request,'accounts/home.html',{'groups':groups, 'user':user})
	
def signup(request):
	return render(request,'accounts/signup.html',{})

def register(request):
	user = User.objects.create_user(request.POST['username'],request.POST['email'],request.POST['password'])
	user.first_name = request.POST['first_name']
	user.last_name = request.POST['last_name']
	user.save()
	goodreadsuser = GRData()
	goodreadsuser.user = user
	goodreadsuser.gr_id = request.POST['gr_id']
	goodreadsuser.token_key = 'null'
	goodreadsuser.token_secret = 'null'
	goodreadsuser.save()
	if request.user.is_authenticated():
		login(request, user)
		usergroups = goodreads.get_user_groups(str(user.grdata.gr_id))
		goodreads.create_group(usergroups, user)
		return HttpResponseRedirect(reverse('members:home',))
	else:
		return HttpResponseRedirect(reverse('members:signin',))
	
def signin(request):
	return render(request,'accounts/signin.html',{})

def login_user(request):
	username = request.POST['username']
	password = request.POST['password']
	user = authenticate(username = username, password=password)
	if user is not None:
		login(request, user)
		usergroups = goodreads.get_user_groups(str(user.grdata.gr_id))
		goodreads.create_group(usergroups, user)
		return HttpResponseRedirect(reverse('members:home',))
	else:
		return HttpResponse('invalid Login')

def log_out(request):
	logout(request)
	return HttpResponseRedirect(reverse('main',))

