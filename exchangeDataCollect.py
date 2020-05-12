import praw
import json
import regex 
import pandas as pd
import numpy as np 
from scipy import stats
from nltk import ngrams
from progressbar import ProgressBar
from collections import OrderedDict

# import helper function 
import helper as h 

G_POSTS = 1000

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



"""
Thoughts 
do ngrams per top user, see what the top 20 posters are primarily selling because we can only get about 1000 posts from the subreddit at once but there 
is not limit when it comes to the total number of posts by individual users. Filter all posts from an individual user by wts, then work off those titles
can cross check top sellers from new posts by total amount of posts  tagged as wts in the subreddit 

multi listings sepearted by commas in the title only comprise around 7% of the posts returned 

need to re-write price finding function, lose about 20% of posts because it can't find the post in the listing
"""
def main():
   connection = h.connect()
   

   redditors = h.topPosters('Watchexchange',connection)
   listing_posts = []
   post_price_list = []
   post_w_price = []

   pbar = ProgressBar()
   for redditor in pbar(redditors):
      listing_posts = listing_posts + h.redditorAnalysis(redditor,connection)

   pbar = ProgressBar()
   for post in pbar(listing_posts):
      list_price = h.price(post)
      if list_price != None:
         post_w_price.append((post,list_price))
   sold = 0
   sum_of_traded_money = 0
   pbar = ProgressBar()
   earliest_sale = 100000000
   for post_tup in pbar(post_w_price):
      if h.saleCheck(post_tup[0]):
         sold += 1
         sum_of_traded_money += post_tup[1]
      sale_time = h.postTime(post_tup[0].created_utc)
      if earliest_sale > sale_time:
         earliest_sale = sale_time
   print("Posts with prices and sold flair : ",sold)
   print("Total money across all listings : ", sum_of_traded_money)
   print("Earliest recording listing in dataset : ", earliest_sale)
   print("Posts with prices : ", len(post_w_price))
   print("Total amount of posts : ",len(listing_posts))
   # here we are at a point where we can start to do some formatting our data
   # we can use the flair to initially check if the item has been sold 
main()