from flask import render_template,Flask,url_for,redirect,request
import numpy as np
from model import (calc_distance,get_user_lat_long,filter_businesses_by_location,filter_by_interest,get_recommendations)
import pickle
from yelp.client import Client
import requests
from gensim.models import Word2Vec

app = Flask(__name__)
app.config.from_object("config")

#with open("gensim_google_news_model","rb") as f:
 #   model = pickle.load(f)
model = Word2Vec.load("model_gensim_bi_gram") 

YELP_API_KEY="dLJpJbvhoFx6LxCYAV-iYzx8xonB-Z-pqtEoSHIdH7cRzg_k788mW1ZJjt73xYS6c1bQuhNqp-TqgSEbX_RYCcdxLJU8AfFdR1MVmCxce2QVeiOBrZ8AryJMTXd5XXYx"


@app.route("/",methods=["POST","GET"]) 
@app.route("/index",methods=["POST","GET"]) 
def home():
    return render_template("index.html")

#@app.route("/recommend",methods=["POST","GET"])
#def vegas_resident():
#    return render_template("recommend.html")

#@app.route("/vegas_visitor",methods=["POST","GET"])
#def vegas_visitor():
#    return render_template("visitor.html")

#@app.route("/vegas_visitor/recommend",methods=["POST","GET"])
#def visitor_recommend():
 #   desired = request.form["what_are_you_looking_for"]
  #  recommendations = get_recommendations(desired) 

@app.route("/recommend",methods=["POST","GET"])
def resident_recommend():
    global model
    looking_for = request.form["what_are_you_looking_for"]
    min_star = request.form["minimum_star_count"]
    address = request.form['street_address']
    #zip_ = request.form['zipcode']
    max_distance = request.form['max_distance'] 
    data = [looking_for,min_star,address,max_distance]  
    recommendations,user_lat_lon,min_star = get_recommendations(data,model)
    #array_recommend = np.array(recommendations)
    #recs = list(array_recommend)
    #print(recs) 
    #recs = recommendations.values.tolist()
    #print(recs)
    list_stars = [0.0,0.5,1.0,1.5,2.0,3.0,3.5,4.0,4.5,5.0]  
    
    yelp_headers={'Authorization': 'Bearer dLJpJbvhoFx6LxCYAV-iYzx8xonB-Z-pqtEoSHIdH7cRzg_k788mW1ZJjt73xYS6c1bQuhNqp-TqgSEbX_RYCcdxLJU8AfFdR1MVmCxce2QVeiOBrZ8AryJMTXd5XXYx'}
    business_ids = recommendations.iloc[:,0].values.tolist()
    recommendations['photo']=0
    for index, id_ in enumerate(business_ids):
        request_get = requests.get(f"https://api.yelp.com/v3/businesses/{id_}",headers=yelp_headers)
        try:
            json_payload = request_get.json()
            photos = json_payload['photos']
            photo = photos[0]
            print(photo)
            recommendations.iloc[index,9]=photo
            #photo_endpoints.append(photos)
        except: 
            #photo_endpoints.append([])
            continue
    recs = recommendations.values.tolist()
    lat = user_lat_lon[0]
    lon = user_lat_lon[1]
    return render_template("recommend.html",recommend=recs,lat=lat,lon=lon,min_star=min_star,list_stars=list_stars, address=address) 

@app.route("/recommend/directions",methods=["POST","GET"])
def direct():
   user_address = request.form.keys()
   address=next(user_address)
   address = address.split("^")
   for index,_ in enumerate(address):
      address[index] += " Las Vegas Nevada"
      address[index] = address[index].split()
      address[index]="+".join(address[index])
      print(address)
   return render_template("directions.html",user_address=address) 


if __name__=="__main__":
    app.run(debug=True) 

