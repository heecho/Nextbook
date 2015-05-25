from django.db import models
from django.contrib.auth.models import User
import requests
import xmltodict
# Create your models here.

class GRData(models.Model):
    user = models.OneToOneField(User)
    gr_id = models.IntegerField(blank=True)
    token_key = models.CharField(max_length = 100)
    token_secret = models.CharField(max_length = 100)

  #   def get_user_groups(self,gr_id,gr_username):

  #   	base_url = "https://www.goodreads.com/group/list"
  #   	user_id = gr_id
  #   	print user_id
  #   	username = gr_username
  #   	key = "1CS3u7goQL5QnUd3GDdYpA"
  #   	if not user_id:
  #   		fetch_url = base_url+".xml"+"?key="+key+"&username="+username
  #   	else:
  #   		fetch_url = base_url+"/"+user_id+".xml"+"?key="+key
  #   		print fetch_url
		
		# xml_data = requests.get(fetch_url).text
		# return xml_data


#def create_recommendations_for_group 
#g = GRData()
#user_groups = g.get_user_groups(self.gr_id,)
# usergroupdict = xmltodict.parse(user_groups)
# groupid = usergroupdict["GoodreadsResponse"]["groups"]['list']["group"]["id"]
# grouptitle = usergroupdict["GoodreadsResponse"]["groups"]['list']["group"]["title"]

