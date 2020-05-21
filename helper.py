import praw
import json
import regex 
import pandas as pd
import numpy as np 
from scipy import stats
from nltk import ngrams
from tqdm import trange, tqdm
from collections import OrderedDict
import _pickle as pickle
import datetime
from csv import reader 

def connect():
    """
    Returns a connection to reddit using account credentials stored in ./creds/redditCreds.json
    """
    with open("creds/redditCreds.json") as f:
        secrets = json.load(f)
        reddit = praw.Reddit(client_id=secrets["client_id"],client_secret=secrets["client_secret"], user_agent=secrets["user_agent"])
    return reddit



def topPosters(subreddit,connection):
   '''
   Takes a subreddit name as a string and praw reddit connectino object
   Returns the 100 top posters based on the most recent 1000 posts in the subreddit
   '''
   reddit = connection
   watch_subreddit = reddit.subreddit(subreddit)
   hot_posts = watch_subreddit.new(limit=1000)
   authors = {}
   for post in tqdm(hot_posts):
      if('post for' not in post.title.lower()):
         if post.author in list(authors.keys()):
            authors[post.author] = authors[post.author] + 1
         else:
            authors[post.author] = 1
   
   # test before deleting 
   # d_descending = OrderedDict(sorted(authors.items(), key=lambda kv: kv[1], reverse=True))
   # sorted_items = sorted(d_descending.items(), key=lambda kv: kv[1], reverse=True)
   
   sorted_items = sorted(authors.items(), key=lambda kv: kv[1], reverse=True)
   redditors = []
   for i in range(150):
      try:
         redditors.append(sorted_items[i][0].name)
      except NoneType:
         print("username is none for some reason")

   return redditors

def redditorAnalysis(user,connection):
   '''
   Takes a string, user, that is the username and a reddit connection object
   returns all posts the user has made in  r/Watchexchange marked as 'wts' 
   '''
   redditor = connection.redditor(user)
   all_submissions = []
   submissions = redditor.submissions.new(limit=None)
   for submission in tqdm(submissions):
      if submission.subreddit.display_name == 'Watchexchange' and 'wts' in submission.title.lower():
         if 'repost' not in submission.title.lower() and ',' not in submission.title and 'bundle' not in submission.title.lower():
            all_submissions.append(submission)
   return all_submissions

def sellPrice(priceStr):
   '''
   takes a string as input and returns the price of the item if the expression can be matched,
   returns None if no expression can be matched
   '''
   num = regex.search(r'[$]\s*[0-9]+[,]*[0-9]*',priceStr)
   num2 = regex.search(r'[0-9]+[,]*[0-9]*[$]',priceStr)
   first = True
   try:
      output = str(num.group(0)).replace('$','')
   except AttributeError:
      first = False
   if not first:
      try:
         output = str(num2.group(0)).replace('$','')
      except AttributeError:
         return None
   output = output.replace(',','')
   return int(output)

def price(post):
   '''
   Takes a praw post object as input and searches the comments for price of the watch 
   If it can find a rpice it will return the integervalue, if it is unable to find a price it will return none
   '''
   comments = post.comments
   for top_level_comment in tqdm(comments):
      if top_level_comment.is_submitter:
         if '$' in top_level_comment.body:
            price = sellPrice(top_level_comment.body)
            if price != None:
               return price
   return None

def saleCheck(post):
   """
   Takes a praw post object as input and returns a boolean value based on whether there is evidence of the 
   watch being sold
   """
   if post.link_flair_text == 'Sold':
      return True
   elif post.link_flair_text == 'Withdrawn':
      return False
   return False

def saveData(data,filename):
    '''
    Takes a data, a list of posts or pandas data frame, and saves it in the given filename and path provided
    '''
    with open('data/'+filename, 'wb') as f:
        pickle.dump(data,f)


def retrieveData(filename):
    '''
    Input is the filename including path to subsection of data and returns the data object 
    '''
    with open('data/'+filename, 'rb') as f:
        mylist = pickle.load(f)
    return mylist

def postTime(post):
    '''
    Takes a praw post object and returns the time that it was posted as three object 
    year as an int, month as an int, and day plus time as a string(will change this later)
    '''
    # when the post was created
    time = post
    time_str = datetime.datetime.fromtimestamp(int(time)).strftime('%Y-%m-%d %H:%M:%S')
    split_time = time_str.split('-')
    return int(split_time[0]),int(split_time[1]), split_time[2]

def extractBrandName(title):
   '''
   input:
      title - string 
   output:
      string 
   idea 1: 
      hard code brands and do string matching on titles 
   idea 2: 
      do some kind of NER(named entity recognition)
   '''
   with open('data/brands/shortList.csv','r') as f:
      csv_reader = reader(f)
      for row in csv_reader:
         if row[0] in title.lower():
            return row[0]
   return 'other'

def getPosts(connection):
   '''
   Collects all of the posts by first looking at the top posters from the 
   newest 1000 posts and then finding all of the posts they've made in the subreddit
   '''
   redditors = topPosters('Watchexchange',connection)
   listing_posts = []
   for redditor in tqdm(redditors):
      listing_posts = listing_posts + redditorAnalysis(redditor,connection)
   return listing_posts

def collectData(time_stamp):
   connection = connect()
   redditors  = topPosters('Watchexchange',connection)
   listing_posts = getPosts(connection)
   saveData(listing_posts,'/rawPosts/' + time_stamp)
   saveData(listing_posts,'/rawPosts/latest')

def createDataSet(posts,filename):
   '''
   Saves a numpy array for future data analysis
   '''
   data = []
   for post in tqdm(posts):
      author = post.author
      title = post.title
      comments = len(post.comments)
      year,month,_ = postTime(post.created_utc)
      list_price = price(post)
      upvotes = post.score
      upvote_ratio = post.upvote_ratio
      sold = saleCheck(post)
      p_row = [author,title,comments,year,month,upvotes,upvote_ratio,sold,list_price]
      with open('data/brands/shortList.csv','r') as f:
         csv_reader = reader(f)
         brand = extractBrandName(post.title)
         for row in csv_reader:
            # if row[0] in title.lower():
            if row[0] == brand:
               p_row.append(1)
            else:
               p_row.append(0)
         if brand == 'other':
            p_row.append(1)
         else:
            p_row.append(0)
      data.append(p_row)
   pdData = pd.DataFrame(data,columns = ['author','title','comments','year','month','upvotes','upvote_ratio','sold','list_price','seiko','tudor','rolex','hamilton','omega','other'])
   saveData(pdData,filename)
   saveData(pdData,'latest')