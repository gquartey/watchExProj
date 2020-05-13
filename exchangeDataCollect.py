from scipy import stats
from collections import OrderedDict
import praw 
import pandas as pd
import helper as h 
import matplotlib.pyplot as plt
from tqdm import trange, tqdm
import time 

"""
thoughts
multi listings sepearted by commas in the title only comprise around 7% of the posts returned 
need to re-write price finding function, lose about 20% of posts because it can't find the post in the listing
"""
def getPosts(connection):
   '''
   Collects all of the posts by first looking at the top posters from the 
   newest 1000 posts and then finding all of the posts they've made in the subreddit
   '''
   redditors = h.topPosters('Watchexchange',connection)
   listing_posts = []
   for redditor in tqdm(redditors):
      listing_posts = listing_posts + h.redditorAnalysis(redditor,connection)
   return listing_posts

def getListingPrice(connection,posts):
   post_w_price = []
   for post in tqdm(listing_posts):
      list_price = h.price(post)
      if list_price != None:
         post_w_price.append((post,list_price))
   return post_w_price

def saleStats(connection,posts):
   '''
   post_w_price is a list of tuples, index 0 is the post, index 1 is the post 
   '''
   sold = 0
   sum_of_traded_money = 0
   earliest_listing = 1000000
   for post in tqdm(posts):
      list_price = h.price(post)
      if list_price != None:
         if h.saleCheck(post):
            sold += 1
            sum_of_traded_money += list_price
      listing_time,_,_ = h.postTime(post.created_utc)
      if earliest_listing > listing_time:
         earliest_listing = listing_time
   print("Posts with prices and sold flair : ",sold)
   print("Total money across all listings : ", sum_of_traded_money)
   print("Earliest recording listing in dataset : ", earliest_listing)

def collectData():
   connection = h.connect()
   redditors  = h.topPosters('Watchexchange',connection)
   listing_posts = getPosts(conenction)
   h.saveData(listing_posts,'/rawPosts/full')
   print("finished updating full dataset")

def createDataSet(posts,filename):
   '''
   Saves a numpy array for future data analysis
   '''
   data = []
   for post in tqdm(posts):
      author = post.author
      title = post.title
      comments = len(post.comments)
      year,month,_ = h.postTime(post.created_utc)
      list_price = h.price(post)
      upvotes = post.score
      upvote_ratio = post.upvote_ratio
      sold = h.saleCheck(post)
      data.append([author,title,comments,year,month,upvotes,upvote_ratio,sold,list_price])
   pdData = pd.DataFrame(data,columns = ['author','title','comments','year','month','upvotes','upvote_ratio','sold','list_price'])
   print(pdData)
   h.saveData(pdData,filename)

def main():
   '''
   This will print out the sample pandas dataframe
   '''

   df = h.retrieveData('analysis/sample')
   print(df)
  

main()