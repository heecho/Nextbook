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


BASE_URL = "https://www.goodreads.com/"
BASE_URL_MEMBERS = BASE_URL + "group/members/"
BASE_URL_BOOKSHELF = BASE_URL + "review/list/"

def build_goodreads_url(base_url):
	return base_url + "?key="+GOODREADS_ACCESS_KEY

def build_members_url(group_id):
	return build_goodreads_url(BASE_URL_MEMBERS+group_id+".xml")

def build_bookshelf_url(userid, shelf, perpage):
	url = "&format=xml"+"&v=2"+"&shelf="+shelf+"&sort=rating"+"&order=d"+"&per_page="+perpage
	return build_goodreads_url(BASE_URL_BOOKSHELF+userid) + url


def get_gr_url(url):
	text_data = requests.get(url).text
	return xmltodict.parse(text_data)


def does_shelf_contain_books(booksonshelf):
	return booksonshelf["GoodreadsResponse"]['reviews'].has_key('review')


def build_one_book_dict(book):
	title = book['book']['title']
	author = book['book']['authors']['author']['name']
	isbn = book['book']['isbn']
	img = "http://covers.openlibrary.org/b/isbn/"+str(isbn)+"-M.jpg"
	gr_book_id = book['book']['id']['#text']
	return (title,{'author':author,'count':1, 'isbn':isbn, 'gr_book_id': gr_book_id, 'image': img})


def for_constraint(some_array):
	return [pound_it(x) for x in some_array]

def build_book_dict(books):

	if type(books) != list:
		return build_one_book_dict(books)

	bookshelfdictionary = {}

	for book in books:
		title, book_dict = build_one_book_dict(book)
		if bookshelfdictionary.has_key(title):
			bookshelfdictionary[title]['count'] = bookshelfdictionary[title]['count']+1
		else:
			bookshelfdictionary[title]= book_dict
	return bookshelfdictionary



def get_user_groups(gr_id):
	base_url = "https://www.goodreads.com/group/list"
	user_id = gr_id
	key = GOODREADS_ACCESS_KEY
	fetch_url = base_url+"/"+user_id+".xml"
	fetch_url = build_goodreads_url(base_url+fetch_url)
	usergroupdict = get_gr_url(fetch_url)
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
	xml_data = requests.get(build_members_url(group_id)).text

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
		if shelf_name == 'read':
			perpage = '20'
		elif shelf_name == 'to-read':
			perpage = '100'

		fetch_url = build_bookshelf_url(singleuser, shelf_name, perpage)
		booksonshelf = get_gr_url(fetch_url)

		if booksonshelf.has_key("GoodreadsResponse"):
			if does_shelf_contain_books(booksonshelf):
				books = booksonshelf["GoodreadsResponse"]['reviews']['review']
				
				bookshelfdictionary = build_book_dict(books)

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

	

