from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Group(models.Model):
	users = models.ManyToManyField(User)
	title = models.CharField(max_length=200)
	gr_group_id = models.IntegerField(unique=True)
	def __str__(self):
		return self.title

class Book(models.Model):
	title = models.CharField(max_length=200)
	author = models.CharField(max_length=200)
	avg = models.IntegerField(blank=True)
	gr_book_id = models.IntegerField()
	cover = models.CharField(max_length=200, default='0')
	def __str__(self):
		return self.title

class Recommendation(models.Model):
	books = models.ManyToManyField(Book)
	group = models.ForeignKey(Group)
	name = models.CharField(max_length=200)
	pubdate = models.DateField(auto_now_add=True)
	def __str__(self):
		return self.name

