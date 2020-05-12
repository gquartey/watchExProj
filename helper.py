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
   '''
   Takes a string, user, that is the username and a reddit connection object
   returns all posts the user has made in  r/Watchexchange marked as 'wts' 
   '''
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
   for top_level_comment in comments:
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

def ngramsWrapper(input, n):
   '''
   Wrapper around built in nltk ngrams function
   Takes a string as input and n is the n-grams number, will return all ngrams from 1 to n as a list of list of strings
   '''
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

