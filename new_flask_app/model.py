import pickle
import pandas as pd
import sqlite3
import requests
import math
from geopy.distance import geodesic
import pickle
import numpy as np
import re

def calc_distance(latitude,longitude,user_lat_lon):
    return geodesic((latitude,longitude),user_lat_lon).miles 
    
def get_user_lat_long(address,city,state):
   address=address.split()
   address="+".join(address)
   city=city.split()
   city="+"+"+".join(city)
   state="+Nevada"
   key="AIzaSyCzfGVD6TDAX8FNOQeeIYcOop59ybS3WTI" 
   request = f"https://maps.googleapis.com/maps/api/geocode/json?address={address},{city},{state}&key={key}"
   response = requests.get(request)
   json_payload=response.json()
   lat_lon = json_payload['results'][0]['geometry']['location']
   lat = lat_lon['lat']
   lon = lat_lon['lng']  
   return (lat,lon)


def filter_businesses_by_location(df,max_distance):
   df = df[df['dist']<float(max_distance)] 
   return df

def filter_by_interest(df,keyword,model):
    #with open("gensim_google_news_model","rb") as f:
    #    model = pickle.load(f)
    keyword = keyword.lower()
    stop_words = re.compile("food|good|close|nearby|best")
    if re.search(stop_words,keyword):
       keyword = re.sub(stop_words,'',keyword)
       keyword = word.strip()
       print(keyword)
    print(keyword)
    if len(keyword.split())==1:
       similar = model.wv.most_similar(keyword,topn=6) 
       words = np.array(similar)[:,0]
       words = np.append(words,keyword) 
       words=list(words)
       words = list(filter(lambda x: len(list(x))>=4,words))  
       reg = re.compile("|".join(words))
       df = df[df['categories'].str.lower().str.contains(reg)]
    elif len(keyword.split())==2:
       keyword = keyword.split()
       keyword = "_".join(keyword)
       similar = model.wv.most_similar(keyword,topn=6)
       words = np.array(similar)[:,0]
       words = np.append(words,keyword)
       words=list(words)
       words = list(filter(lambda x: len(list(x))>=4,words))
       reg = re.compile("|".join(words))
       df = df[df['categories'].str.lower().str.contains(reg)]
	 
    return df


def get_recommendations(input_,model):
   keyword = input_[0]
   min_star = input_[1]
   address = input_[2]
   #zip_  = input_[3]
   max_distance=input_[3]
   con = sqlite3.connect("yelp.db")
   df_interest = pd.read_sql_query("SELECT business_id,name,neighborhood,address,city,state,postal_code,latitude,longitude,stars,review_count,categories FROM vegas_business",con)
   user_lat_lon = get_user_lat_long(address,"Las Vegas","Nevada")
   df_interest['dist'] = df_interest.apply(lambda x: calc_distance(
                                           x['latitude'],
                                           x['longitude'],
                                           user_lat_lon)
                                           ,axis=1) 
                                           
   df_interest = filter_businesses_by_location(df_interest,max_distance)
   df_interest = filter_by_interest(df_interest,keyword,model)
   df_interest['score_reviews'] = ((df_interest['stars']-df_interest['stars'].mean())/df_interest['stars'].std())*((df_interest['review_count']-df_interest['review_count'].mean())/df_interest['review_count'].std()) 
   df_interest = df_interest.sort_values(by="score_reviews",ascending=False)
   df_interest['dist'] = np.round(df_interest['dist'],2)
   return df_interest[['business_id','name','neighborhood','address','stars','review_count','dist','latitude','longitude']].iloc[:5,:],user_lat_lon,min_star  
    


