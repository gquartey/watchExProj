import helper as h
from datetime import datetime

def main():
   '''
   This function 
   '''
   today = datetime.now()
   time_stamp = today.strftime("%Y-%m-%d")
   h.collectData(time_stamp)

   posts = h.retrieveData('rawPosts/' + time_stamp)
   h.createDataSet(posts,'analysis/' + time_stamp)
   df = h.retrieveData('analysis/' + time_stamp)

   df.to_csv(r'data/analysisCSV/' + time_stamp + '.csv')
   df.to_csv(r'data/analysisCSV/' + 'latest.csv')

main()