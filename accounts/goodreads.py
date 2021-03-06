import requests
import xmltodict
from accounts.models import GRData
from django.contrib.auth.models import User
from groups.models import Book, Group, Recommendation
import json
from collections import OrderedDict
import random
from django.utils import timezone
import os

GOODREADS_ACCESS_KEY = os.environ.get("GOODREADS_ACCESS_KEY")


def get_user_groups(gr_id):
	base_url = "https://www.goodreads.com/group/list"
	user_id = gr_id
	key = GOODREADS_ACCESS_KEY
	fetch_url = base_url+"/"+user_id+".xml"+"?key="+key
	xml_data = requests.get(fetch_url).text
	usergroupdict = xmltodict.parse(xml_data)
	#print usergroupdict
	group_ids = {}
	group_id = usergroupdict["GoodreadsResponse"]["groups"]['list']["group"]
	if type(group_id) == list:
		for group in group_id:
			gr_group = group["id"]
			gr_name = group['title']
			group_ids[gr_name] = gr_group
	else:
		gr_name = group_id['title']
		group_ids[gr_name]=group_id['id']
	#print group_ids
	return group_ids

def gr_get_group_members(group_id):
	base_url = "https://www.goodreads.com/group/members/"
	groupid = group_id
	key = GOODREADS_ACCESS_KEY
	fetch_url = base_url+groupid+".xml"+"?key="+key
	#print fetch_url
	xml_data = requests.get(fetch_url).text
	#print xml_data
	groupmembersdict = xmltodict.parse(xml_data)
	group_users = groupmembersdict["GoodreadsResponse"]["group_users"]["group_user"]
	users = {}
	for user in group_users:
		user_name = user["user"]["first_name"]
		user_id = user["user"]["id"]["#text"]
		users[user_name]=user_id
	#print users
	return users

def get_bookshelf_contents(user_ids,shelf_name):
	userids = []
	bookshelfdictionary = {}
	for x in user_ids:
		gr_id = user_ids[x]
		userids.append(gr_id)
	for singleuser in userids:
		base_url = "https://www.goodreads.com/review/list/"
		userid = singleuser
		shelf = shelf_name
		if shelf == 'read':
			perpage = '20'
		elif shelf == 'to-read':
			perpage = '100'
		key = GOODREADS_ACCESS_KEY
		fetch_url = base_url+userid+"?format=xml"+"&key="+key+"&v=2"+"&shelf="+shelf+"&sort=rating"+"&order=d"+"&per_page="+perpage
		xml_data = requests.get(fetch_url).text
		booksonshelf = xmltodict.parse(xml_data)
		if booksonshelf.has_key("GoodreadsResponse"):
			if booksonshelf["GoodreadsResponse"]['reviews'].has_key('review'):
				books = booksonshelf["GoodreadsResponse"]['reviews']['review']
				if type(books)== list:
					for book in books:
						title = book['book']['title']
						author = book['book']['authors']['author']['name']
						isbn = book['book']['isbn']
						img = "http://covers.openlibrary.org/b/isbn/"+str(isbn)+"-M.jpg"
						gr_book_id = book['book']['id']['#text']
						if bookshelfdictionary.has_key(title):
							bookshelfdictionary[title]['count']= bookshelfdictionary[title]['count']+1
						else:
							bookshelfdictionary[title]={'author':author,'count':1, 'isbn':isbn, 'gr_book_id': gr_book_id, 'image': img}
				else:
					title = books['book']['title']
					author = books['book']['authors']['author']['name']
					isbn = books['book']['isbn']
					img = "http://covers.openlibrary.org/b/isbn/"+str(isbn)+"-M.jpg"
					gr_book_id = books['book']['id']['#text']
					if bookshelfdictionary.has_key(title):
							bookshelfdictionary[title]['count']= bookshelfdictionary[title]['count']+1
					else:
						bookshelfdictionary[title]={'author':author,'count':1, 'isbn':isbn, 'gr_book_id': gr_book_id, 'image': img}
	#print bookshelfdictionary
	return bookshelfdictionary

def check_duplicates(dictionary):
	#takes in dictionary of {title: {'author':author, 'count': #}}
	duplicate_titles = {}
	for x in dictionary:
		if dictionary[x]['count'] > 1:
			duplicate_titles[x] = {'author': dictionary[x]['author'], 'isbn': dictionary[x]['isbn'], 'gr_book_id':dictionary[x]['gr_book_id'], 'image': dictionary[x]['image']} 	
	if len(duplicate_titles) > 0:
		#print duplicate_titles
		return duplicate_titles
	else:
		#print dictionary
		return dictionary

def gr_similar_title(dictionary):
	isbns = []
	for x in dictionary:
		isbns.append(dictionary[x]['isbn'])
	print isbns
	similar_titles = {}
	for x in range(0,len(isbns)):
		base_url = "https://www.goodreads.com/book/isbn"
		isbn = isbns[x]
		#print isbn
		key = GOODREADS_ACCESS_KEY
		if type(isbn)== unicode:
			fetch_url = base_url+"?key="+key+"&isbn="+isbn
			xml_data = requests.get(fetch_url).text
			similartitlesdict = xmltodict.parse(xml_data)
			if similartitlesdict['GoodreadsResponse']['book'].has_key('similar_books'):
				similar_books = similartitlesdict["GoodreadsResponse"]["book"]['similar_books']['book']
				for book in similar_books:
					book_title = book['title']
					book_author = book['authors']['author']['name']
					book_id = book['id']
					img = book['image_url']
					book_avg = book['average_rating']
					if book_avg > 3.5:
						similar_titles[book_title]={'author':book_author, 'avg': book_avg, 'gr_book_id': book_id, 'image': img}
	#print similar_titles
	return similar_titles

			
def run_rec(groupid):
	members = gr_get_group_members(groupid)
	to_read_books = get_bookshelf_contents(members, 'to-read')
	to_read_duplicates = check_duplicates(to_read_books)
	read_books = get_bookshelf_contents(members, 'read')
	read_duplicates = check_duplicates(read_books)
	#print read_duplicates
	get_similar = gr_similar_title(read_duplicates)
	#print get_similar
	rec_titles_to_read = {}
	rec_similar_titles = []
	for x in to_read_duplicates:
		rec_titles_to_read[x] = {'author': to_read_duplicates[x]['author'], 'gr_book_id': to_read_duplicates[x]['gr_book_id'], 'image':to_read_duplicates[x]['image']}
	for x in get_similar:
		rec_similar_titles.append(x)
	random.shuffle(rec_similar_titles)
	#print rec_similar_titles
	to_read_length = len(rec_titles_to_read)
	if to_read_length > 20:
		recommendation = rec_titles_to_read
	elif to_read_length < 20:
		fill = 20 - to_read_length
		recommendation = rec_titles_to_read
		fill_books = rec_similar_titles[0:fill]
		for x in fill_books:
			recommendation[x] = {'author':get_similar[x]['author'], 'avg':get_similar[x]['avg'], 'gr_book_id':get_similar[x]['gr_book_id'], 'image': get_similar[x]['image']}
	#print recommendation
	return recommendation


#run_rec('163349')
def create_group(usergroups, user):
	#existing = user.group_set.all()
	existing = Group.objects.all()
	for x in usergroups:
		if not existing.filter(gr_group_id = int(usergroups[x])).exists():
			group = Group()
			group.gr_group_id = int(usergroups[x])
			group.title = x
			group.save()
			group.users.add(user)
		else:
			group = Group.objects.get(gr_group_id = usergroups[x])
			group.users.add(user)

def create_books(dictionary):
	existing = Book.objects.all()
	books = []
	for x in dictionary:
		if not existing.filter(gr_book_id = dictionary[x]['gr_book_id']).exists():
			book = Book()
			book.title = x
			book.author = dictionary[x]['author']
			book.avg = 3
			book.cover = dictionary[x]['image']
			print book.cover
			book.gr_book_id = dictionary[x]['gr_book_id']
			book.save()
			books.append(book)
		else:
			books.append(Book.objects.get(gr_book_id=dictionary[x]['gr_book_id']))
	return books
	
def create_rec(book_array,title,group):
	r = Recommendation()
	r.name = title
	r.group = group
	r.save()
	for x in book_array:
		r.books.add(x)
	r.save()
	print r.books
	return r

	

