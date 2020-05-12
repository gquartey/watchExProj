import praw
import json
import regex 
import pandas as pd
import numpy as np 
from scipy import stats
from nltk import ngrams
from progressbar import ProgressBar
from collections import OrderedDict
import _pickle as pickle
import datetime

G_POSTS = 1000

def connect():
    """
    Returns a connection to reddit using account credentials 
    """
    with open("creds/redditCreds.json") as f:
        secrets = json.load(f)
        reddit = praw.Reddit(client_id=secrets["client_id"],client_secret=secrets["client_secret"], user_agent=secrets["user_agent"])
    return reddit



def topPosters(subreddit,connection):
   '''
   returns a list of top posters from a given subreddit based on the most recent 1000 posts
   '''
   reddit = connection
   watch_subreddit = reddit.subreddit(subreddit)
   hot_posts = watch_subreddit.new(limit=1000)
   authors = {}
   acc = 0 
   for post in hot_posts:
      acc += 1
      if('post for' not in post.title.lower()):
         if post.author in list(authors.keys()):
            authors[post.author] = authors[post.author] + 1
         else:
            authors[post.author] = 1
   
   d_descending = OrderedDict(sorted(authors.items(), key=lambda kv: kv[1], reverse=True))

   sorted_items = sorted(d_descending.items(), key=lambda kv: kv[1], reverse=True)
   things = list(authors.keys())
   redditors = []
   for i in range(100):
      redditors.append(sorted_items[i][0].name)
   return redditors

def redditorAnalysis(user,connection):
   reddit = connection
   redditor = reddit.redditor(user)
   all_submissions = []
   submissions = redditor.submissions.new(limit=None)
   for submission in submissions:
      if submission.subreddit.display_name == 'Watchexchange' and 'wts' in submission.title.lower():
         if 'repost' not in submission.title.lower() and ',' not in submission.title and 'bundle' not in submission.title.lower():
            all_submissions.append(submission)
   return all_submissions

def sellPrice(priceStr):
   # needs some regular expression magic here
   # find a more effecient way of doing the below
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
   comments = post.comments
   for top_level_comment in comments:
      if top_level_comment.is_submitter:
         if '$' in top_level_comment.body:
            price = sellPrice(top_level_comment.body)
            if price != None:
               return price
   return None

def saleCheck(post):
   """
   Return true/false based on whether the watch has been sold or not 

   Need to add in more thorough checks if an item is sold, 
   """
   if post.link_flair_text == 'Sold':
      return True
   elif post.link_flair_text == 'Withdrawn':
      return False
   return False

def saveData(data,filename):
    '''
    Saves a copy of listings and their price as a list in a file
    '''
    with open('data/'+filename, 'wb') as f:
        pickle.dump(data,f)


def retrieveData(filename):
    '''
    Input is the filename where the listings were saved, must be a string
    '''
    with open('data/'+filename, 'rb') as f:
        mylist = pickle.load(f)
    return mylist

def postTime(post):
    '''
    initially will just return the year that a post was created in, then will expand this to get 
    more granular information
    '''
    # when the post was created
    time = post
    time_str = datetime.datetime.fromtimestamp(int(time)).strftime('%Y-%m-%d %H:%M:%S')
    split_time = time_str.split('-')
    return int(split_time[0]),int(split_time[1]), split_time[2]

def ngramsWrapper(input, n):
   input = input.lower()
   unwantedStrings = ['[wts]','[wts/wtt]','[wts]/[wtt]','[wtt]','[meta]','[wtb]','and','automatic','with','dial','vintage','full','-','&','blue','strap','black','watch','new','kit',',']
   for i in unwantedStrings:
      input = input.replace(i,'')
   input = input.split(' ')
   if '' in input:
      input.remove('')
   if ' ' in input: 
      input.remove(' ')
   output = []
   for i in range(1,n+1):
      for k in ngrams(input,i):
         output.append(list(k))
   return output

