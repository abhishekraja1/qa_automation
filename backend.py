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
from bson.json_util import dumps
from bson import json_util, ObjectId
import json
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)


app.config['MONGO_DBNAME'] = 'webtracker'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/webtracker'

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
@app.route('/check_manager/<name>', methods=['GET'])
def check_manager(name):
  manager_check = mongo.db.intranet_bulk
  login_user = manager_check.find_one({'companyEmail' : name})
  if login_user:
    login_user_id =login_user['userId']
    if (manager_check.find_one({'manager.userId' : login_user_id})):
      return jsonify({'result' : 'manager'})
    return jsonify({'result' : 'no record found'})
  return jsonify({'result' : 'others'})

  
#api to get intranet details
#api to get intranet details
@app.route('/get_intranet_details', methods=['GET'])
def get_intranet_details():
     intranet_bulk_collection = mongo.db.intranet_bulk
     url = 'https://intranet.terralogic.com/public/api/getemployeesbylocation'
     payload = {
     "location": "INDIA",
     "start": 0,
     "limit": 420
     }
     headers = {'content-type': 'application/json'}
     requestpost = requests.post(url, data=json.dumps(payload), headers=headers)
     response_data = requestpost.json()
     for i in response_data["data"]["users"]:
       if (intranet_bulk_collection.find_one(json_util._json_convert(i))):
           intranet_bulk_collection.update({"userId" :i['userId']},{"$set": json_util._json_convert(i)})
       else:    
          intranet_bulk_collection.insert(json_util._json_convert(i))
    
     return  jsonify({'result' : response_data})
    
# to fetch particular employee details using PSI-ID
@app.route('/get_particular_emp_details/<eid>', methods=['GET'])
def get_single_emp_detail(eid):
      intranet_dummy_collection = mongo.db.intranet_dummy_collection
      emp_sin_data = intranet_dummy_collection.find_one({'userId' : eid})
      if emp_sin_data:
        return json.dumps(emp_sin_data,cls=JSONEncoder)
      else:
        return  jsonify({'result' : 'no data found'})

      return jsonify({'result' : 'null'})
        

# to update particular employee details from UI
@app.route('/update_particular_emp_details', methods=['POST'])
def update_single_emp_detail():
      if request.get_json():
        data = request.get_json()
        required_fields = ['userId', 'emp_emailid', 'emp_jobtitle', 'emp_mng_username', 'emp_mng_userid',
        'emp_projectid', 'emp_projectname','emp_firstname', 'emp_lastname'
        ]
        user_keys = data.keys()
        if required_fields.sort() == list(set(required_fields) & set(user_keys)).sort():
             intranet_dummy_collection = mongo.db.intranet_dummy_collection
             emp_sin_data = intranet_dummy_collection.find_one({'userId' :data['userId']})
             if emp_sin_data:
                 intranet_dummy_collection.update({"userId" :data['userId']},{"$set":{
                 "userId":data['userId'],
                 "companyEmail":data['emp_emailid'],
                 "jobTitle":data['emp_jobtitle'],
                 "manager.userName":data['emp_mng_username'],
                 "manager.userId":data['emp_mng_userid'],
                 "project.projectId":data['emp_projectid'],
                 "project.projectName":data['emp_projectname'],
                 "userName":data['emp_firstname'] +" "+data['emp_lastname'],
                 } })
                 result =intranet_dummy_collection.find_one({'userId' : data['userId']})
                 return jsonify({'result' : 'successfully updated' })  
             else:
                 return jsonify({'result' : 'fields not getting updated updated' })  

      return jsonify({'result' : 'required fields are missing'})

# to get/add particular employee skills from UI
@app.route('/particular_skills/<eid>', methods=['POST'])
def emp_skill_detail(eid):
      payload={
      "userId":eid,
      "userName":request.json['userName'],
      "skills" :request.json['skills']
      }
      skill=request.json['skills']
      if(mongo.db.skills_master.find({"userId":eid}).count()!=0):
          for i in skill:
            skillset=i['skillName']
            print(skillset)
            skills_dummy_collection = mongo.db.skills_master.find({"$and":[{"userId": eid},{"skills.skillName":skillset}]})
            print(skills_dummy_collection.count())
            if (skills_dummy_collection.count()!=0  and i['DomainName'] != None and i['skillName'] != None and i['months'] != None and i['level'] != None and i['CertificationStatus'] != None ):
              mongo.db.skills_master.update({"userId":eid,"skills.skillName": skillset
                }, {
                  "$set": {
                  "skills.$":
                    {'DomainName': i['DomainName'],
                    'skillName': i['skillName'],
                    'months': i['months'],
                    'level': i['level'],
                    'CertificationStatus': i['CertificationStatus']}
                        
                      } 
                    })
              print("if")
            else:
              if(i['DomainName'] != None and i['skillName'] != None and i['months'] != None and i['level'] != None and i['CertificationStatus'] != None):
                mongo.db.skills_master.update({'userId': eid,'skills.skillName': { "$not": { '$elemMatch' : { 'skills.skillName' : skillset}}}
                }, {
                  "$addToSet": {
                  "skills":{'DomainName': i['DomainName'],
                    'skillName': i['skillName'],
                    'months': i['months'],
                    'level': i['level'],
                    'CertificationStatus': i['CertificationStatus']}
                        
                      
                          }
                  })
                print(skill)
                print("else")             
      else:
          if(request.json['userId'] == eid):
            mongo.db.skills_master.insert(payload)
            print(payload)
          else:
            return jsonify({'invalid details'})
      result = mongo.db.skills_master.find_one({'userId':eid})
      return json.dumps(result,cls=JSONEncoder)

#for getting skills from DB
@app.route('/get_particular_skills/<eid>',methods=['GET'])
def get_emp_skills(eid):
      emp_skill_data = mongo.db.skills_master.find_one({'userId' : eid})
      if emp_skill_data:
        return json.dumps(emp_skill_data,cls=JSONEncoder)
      else:
        return  jsonify({'result' : 'no data found'})
      return jsonify({'result' : 'null'})

#delete particular skills
@app.route('/delete_particular_skills/<eid>',methods=['POST'])
def delete_emp_skills(eid):
      skillName = request.json['skillName']
      if(mongo.db.skills_master.find({"userId":eid}).count()!=0):
        delete_skillset = mongo.db.skills_master.update({"userId":eid},{"$pull":{"skills":{"skillName":skillName}}})            
        print(delete_skillset)
      return jsonify({'result' : 'deleted succesfully'}) 

#Add or update project Details
@app.route('/project_details', methods=['POST'])
def projects_detail():
      project_Skills =[]
      project_Technique =[]
      project_Skills=request.json['Skill_Set']
      project_Technique = request.json['Technique']
      payload={
      "Customer_Details" : request.json['Customer_Details'],
	    "Project_Id" : request.json['Project_Id'],
      "Project_Fullname" : request.json['Project_Fullname'],
      "Project_Shortname" : request.json['Project_Shortname'],
      "Biz_Code" : request.json['Biz_Code'],
      "Project_Status" : request.json['Project_Status'],
      "Project_Type" : request.json['Project_Type'],
      "Project_Manager" : request.json['Project_Manager'],
      "Group" : request.json['Group'],
      "DomainName" : request.json['DomainName'],
      "Start_Date" : request.json['Start_Date'],
      "End_Date" : request.json['End_Date'],
      "Suspended_Date" : request.json['Suspended_Date'],
      "Engaging_Date" : request.json['Engaging_Date'],
      "Estimation_Effort" : request.json['Estimation_Effort'],
      "Spent_Effort" : request.json['Spent_Effort'],
      "Current_Billable_Headcount" : request.json['Current_Billable_Headcount'],
      "Technique" : project_Skills,
      "Skill_Set" : project_Technique,
      "Project_Description" : request.json['Project_Description'],
      "Note" : request.json['Note']

      }
      if(mongo.db.projects_master.find({"Project_Id":request.json['Project_Id']}).count()!=0):
          mongo.db.projects_master.update({"Project_Id":request.json['Project_Id']
                          }, {
                  "$set": payload
                    })
          return jsonify({"result":"Project Updated Succesfully"})
      else:
          if(mongo.db.projects_master.find({"Project_Id":request.json['Project_Id']}).count()==0 and request.json['Project_Id']!= None):
              mongo.db.projects_master.insert(payload)
              return jsonify({"result":"Project Details Inserted Succesfully"})

#for getting project details from DB using project ID
@app.route('/get_particular_project_details/<eid>', methods=['GET'])
def get_project_details(eid):
      print(eid)
      print(type(eid))
      print(mongo.db.projects_master.find_one({'Project_Id' : eid}))
      project_data = mongo.db.projects_master.find_one({'Project_Id' : int(eid)})
      print(project_data)
      if project_data:
        return json.dumps(project_data,cls=JSONEncoder)
      else:
        return  jsonify({'result' : 'no data found'})
#for getting ADM employees from DB 
@app.route('/get_adm_employee_details', methods=['GET'])
def get_adm_employee_details():
      adm_data = mongo.db.intranet_dummy_collection.find({"groupName":"Application Development"},{"userId":1,"project.projectId":1,"_id":0})
      print(adm_data.count())
      adm_emp_count=[]
      for i in adm_data:
        print(i['userId'])
        adm_emp_count.append(userId)
        print(type(adm_data))
        if adm_data:
          return json.dumps(list(adm_data).json,cls=JSONEncoder)
        else:
          return  jsonify({'result' : 'no data found'}) 
      print(len(adm_emp_count))     
     
if __name__ == '__main__':
    app.run(debug=True,port=5000)
