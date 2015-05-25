from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils import timezone
from accounts.models import GRData
from groups.models import Book, Group, Recommendation
from accounts import goodreads
from django.contrib.auth import authenticate, login, logout
from django.template.defaulttags import register
# Create your views here.

def home(request, group_id):
	user = request.user
	members = goodreads.gr_get_group_members(group_id)
	groups = Group.objects.filter(gr_group_id = group_id)
	this_group = groups[0]
	return render(request,'groups/home.html',{'members':members, 'group': this_group})

def run_rec(request,group_id):
	groups = Group.objects.filter(gr_group_id = group_id)
	group = groups[0]
	title = request.POST['title']
	get_recs = goodreads.run_rec(str(group.gr_group_id))
	#print get_recs
	books = goodreads.create_books(get_recs)
	print books
	recommendation = goodreads.create_rec(books, title, group)
	rec_id = recommendation.id
	return HttpResponseRedirect(reverse('groups:showrec', args=(group_id,rec_id)))

def show_rec(request, group_id, rec_id):
	groups = Group.objects.filter(gr_group_id = group_id)
	this_group = groups[0]
	recommendation = Recommendation.objects.get(id=rec_id)
	title = recommendation.name
	bookset = recommendation.books.all()
	print bookset
	allrecs = Recommendation.objects.filter(group = this_group.id).order_by('-pubdate')
	return render(request,'groups/recommendation.html',{'books':bookset, 'group': this_group, 'title':title, 'allrecs': allrecs})
	#return HttpResponse('recommendation')

def my_rec(request):
	user = request.user
	groups = user.group_set.all()
	group_recs = {}
	for this_group in groups:
		group_recs[this_group] = Recommendation.objects.filter(group = this_group.id).order_by('-pubdate')
	return render(request,'groups/myrecommendations.html',{'user': user, 'group_recs': group_recs})

@register.filter
def get_item(dictionary,key):
	return dictionary.get(key)
	

