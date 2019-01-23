from flask import Flask
from flask import jsonify
from flask import request
from pymongo import MongoClient
from flask_pymongo import PyMongo
import json
from flask import Response
from flask import Response
import requests
import simplejson
from bson import ObjectId
from bson import ObjectId
import simplejson as json
from flask import jsonify,make_response
from flask import Flask,render_template,flash,redirect,url_for,session,logging
import time
import atexit
import re
from bson.json_util import dumps
from bson import json_util, ObjectId
import json
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)


app.config['MONGO_DBNAME'] = 'qa_automation'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/qa_automation'

mongo = PyMongo(app)
# from employee_schema import validate_user
@app.route('/', methods=['GET'])
def empty_route():
  return render_template('list.html')

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)
  
 #to check the manager details

#delete particular skills
@app.route('/Weekly_Data',methods=['POST'])
def Weekly_Details():
      From_Date = request.json['from_Date']
      To_Date = request.json['to_Date']
      print(From_Date)
      p=From_Date.split("-")
      print(p[0])
      reslut = mongo.db.Testcase_Details.find({"TimeStamp":{"$gt":From_Date,"$lt":To_Date}})
      result= json_util._json_convert(reslut)
      return jsonify({'result' : result}) 


  
 #to check the QA details
@app.route('/TestCase_Details/<Particular_Date>', methods=['GET'])
def check_manager(Particular_Date):
  Paticular_Day_Details = mongo.db.Testcase_Details
  Day_wise_Details = Paticular_Day_Details.find({'TimeStamp' :{'$regex':Particular_Date}})
  if Day_wise_Details:
    return jsonify({'result' : json_util._json_convert(Day_wise_Details)})
  else:
        return  jsonify({'result' : 'no data found'})
  
     
if __name__ == '__main__':
    app.run(debug=True,port=5000)
