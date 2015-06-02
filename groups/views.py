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
from django.contrib.auth.decorators import login_required
from rq import Queue
from worker import conn


# Create your views here.

@login_required(login_url='members:signin')
def home(request, group_id):
	user = request.user
	members = goodreads.gr_get_group_members(group_id)
	groups = Group.objects.filter(gr_group_id = group_id)
	this_group = groups[0]
	return render(request,'groups/home.html',{'members':members, 'group': this_group})

def run_rec(request,group_id):
	title = request.POST['title']
	groups = Group.objects.filter(gr_group_id = group_id)
	group = groups[0]
	get_recs = goodreads.run_rec(str(group.gr_group_id))
	books = goodreads.create_books(get_recs)
	recommendation = goodreads.create_rec(books, title, group)
	rec_id = recommendation.id
	return HttpResponseRedirect(reverse('groups:showrec', args=(group_id,rec_id)))

	#q = Queue(connection=conn)
	#job = q.enqueue(api_call, [group_id,title])
	# print "job",job.get_id()
	# value = "job-result" + str(job.get_id())
	# value += str(job.result)
	#return HttpResponseRedirect(reverse('myrec',))

def api_call(info):
	# f = "/Users/hannah/Documents/Capstone/bookclubv2/nextbook/jobsresult"
	# f2 = open(f,"w")
	# f2.write(group_id[1])
	# f2.close()
	groups = Group.objects.filter(gr_group_id = info[0])
	group = groups[0]
	get_recs = goodreads.run_rec(str(group.gr_group_id))
	books = goodreads.create_books(get_recs)
	recommendation = goodreads.create_rec(books, info[1], group)

def show_rec(request, group_id, rec_id):
	groups = Group.objects.filter(gr_group_id = group_id)
	this_group = groups[0]
	recommendation = Recommendation.objects.get(id=rec_id)
	title = recommendation.name
	bookset = recommendation.books.all()
	print bookset
	allrecs = Recommendation.objects.filter(group = this_group.id).order_by('-pubdate')[0:11]
	return render(request,'groups/recommendation.html',{'books':bookset, 'group': this_group, 'title':title, 'allrecs': allrecs})
	#return HttpResponse('recommendation')

@login_required(login_url='members:signin')
def my_rec(request):
	user = request.user
	groups = user.group_set.all()
	print groups
	group_recs = {}
	recs = Recommendation.objects.filter(group = groups[0].id)
	print recs
	for this_group in groups:
		group_recs[this_group] = Recommendation.objects.filter(group = this_group.id).order_by('-pubdate')
	print group_recs
	return render(request,'groups/myrecommendations.html',{'user': user, 'group_recs': group_recs})

@register.filter
def get_item(dictionary,key):
	return dictionary.get(key)


