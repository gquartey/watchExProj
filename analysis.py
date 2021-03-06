import praw
import helper as h
import numpy as np
from matplotlib import pyplot as plt
from tqdm import trange, tqdm
from collections import OrderedDict


G_POSTS = 1000
sub = 'Watchexchange'
def trendingBrands(connection):  
   # create a reddit object
   reddit = connection

   # example of getting posts from a subreddit
   # watch_subreddit = reddit.subreddit(sub)
   # hot_posts = watch_subreddit.hot(limit=G_POSTS)
   redditors = h.topPosters(sub,connection)
   posts = []
   for redditor in tqdm(redditors):
      posts = posts + h.redditorAnalysis(redditor,reddit)
   master_ngram = {}
   for post in tqdm(posts):
      if('Post for' not in post.title):
         n_grams = h.ngramsWrapper(post.title,3)
         for i in n_grams:
            substring = " ".join(i)
            if substring != '' and substring != ' ':
               if substring in list(master_ngram.keys()):
                  master_ngram[substring] = master_ngram[substring] + 1
               else:
                  master_ngram[substring] = 1

   d_descending = OrderedDict(sorted(master_ngram.items(), key=lambda kv: kv[1], reverse=True))
    
   things = list(d_descending.keys())
   for i in range(50):
      print(things[i])

def priceStats():
   # have to look into how to iterate through comments to get the prices that the watches are listed for
   # going through comments to find the listed prices of watches on the subreddit 
   reddit = connect()
   watch_subreddit = reddit.subreddit('WatchExchange')
   hot_posts = watch_subreddit.hot(limit=G_POSTS)
   list_prices = []
   print("started collecting data and prices")
   for post in tqdm(hot_posts):
      if('wts' in post.title.lower()):
         comments = post.comments
         for top_level_comment in comments:
            split = top_level_comment.body.split()
            for substring in split:
               if '$' in substring:
                  price = h.sellPrice(substring)
                  if price != None:
                     list_prices.append(price)
   print("finished collecting data and prices")
   arr = np.array(list_prices)
   print("Avg listing price: ", np.around(np.average(arr),decimals=2))
   print("Highest listing price: ", float(np.max(arr)))
   print("Median listing price: ",np.median(arr))
   print("Amount of total sale listings: ", len(arr))
   sorted_arr = np.sort(arr)
   x = range(0,len(sorted_arr))
   plt.yscale("log")
   plt.title("List prices from r/WatchExchange")
   plt.xlabel("Listing number")
   plt.ylabel("Price")
   plt.plot(x,sorted_arr)
   plt.show()

con = h.connect()
trendingBrands(con)