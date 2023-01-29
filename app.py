from flask import Flask, jsonify, make_response, request
import json
from flask_sock import Sock

######################################

jsonFile = "Jobs.json"
stylistjson = "Stylist.json"

########## Read jobs from json file
with open(jsonFile) as job_file:
  file_contents = job_file.read()
print(file_contents)
job_file.close()

Jobs = json.loads(file_contents)
print(Jobs)


########## Read stylist from json file

with open(stylistjson) as st_file:
  file_contents = st_file.read()
print(file_contents)
st_file.close()

Stylists = json.loads(file_contents)
print(Stylists)

###########################################

app = Flask(__name__)
sock = Sock(app)
@app.route("/")
def home():
    return "<h1>Home Page<h1>"    

   
@app.route("/about")
def about():
    return "<h1>About Page Arghavan<h1>"  


@app.route("/jobs", methods=["GET"])
def get_jobs():    
    return make_response(jsonify(Jobs))


@app.route("/jobs/<name>", methods = ['GET'])
def get_job_by_stylist(name):
    stylist=[]
    for job in Jobs:
        if job["Stylist"] == name:
            stylist.append(job)
    return jsonify(stylist)


@app.route("/jobs/<int:id>", methods= ['GET'])
def get_job_by_id(id):
    for job in Jobs:
        if job["ID"] == id:  
            return jsonify(job)
    
    
@app.route('/jobs/<int:id>', methods= ['PUT'])
def update_job_status(id):
    for job in Jobs:
        if job["ID"] == id:  
            print(job)
            job["Finished"] = request.json.get("Finished", job["Finished"])
            print(job)
            with open(jsonFile, "w+") as f:
                json.dump(Jobs, f)
            f.close()
            return jsonify(job)  


@app.route('/jobs/assign/<int:id>', methods= ['GET'])
def assign_job(id):
    for job in Jobs:
        if (job["ID"] == id): 
            print(job)
            name=job["Stylist"]
            for st in Stylists:
                if (st["Name"]==name and job["Status"]=="Undone"):
                    job["Status"] = "Assigned"
                    job["QNumber"]= st["QPerson"]+1
                    st["QPerson"]= st["QPerson"]+1
                    st["QWating"]= st["QWating"]+job["Duration"]                   
                    job["QWating"]=st["QWating"]-job["Duration"] 
                    with open(jsonFile, "w+") as f:
                        json.dump(Jobs, f)
                    f.close()
                    with open(stylistjson, "w+") as f:
                        json.dump(Stylists, f)
                    f.close()                   
            return jsonify(job)


@app.route("/jobs/accept/<int:id>", methods= ['GET'])
def accept(id):
    for job in Jobs:        
        if (job["ID"] == id and job["Status"]=="Assigned"): 
            name=job["Stylist"]
            for st in Stylists:
                if (st["Name"]==name and st["Status"]=="Ready"):
                    jobac=job
                    job["Status"]= "Ongoing"
                    st["Status"]="Busy"
                    job["QNumber"]=job["QNumber"]-1
                    st["QPerson"]=st["QPerson"]-1
                    job["QWating"]=0 
                    break
    name=jobac["Stylist"]
    print(name)
    for job in Jobs: 
        if(job["ID"] != id and job["Status"]=="Assigned" and job["Stylist"]==name):
            job["QNumber"]=job["QNumber"]-1
            print('********')
            print(job)
    with open(jsonFile, "w+") as f:
        json.dump(Jobs, f)
    f.close()
    with open(stylistjson, "w+") as f:
        json.dump(Stylists, f)
    f.close()
    print(jobac)     
    return jsonify(jobac)


@app.route('/jobs/finish/<int:id>', methods= ['GET'])
def finish_job(id):
    for job in Jobs:
        if (job["ID"] == id and job["Status"]=="Ongoing"): 
            name=job["Stylist"]
            for st in Stylists:
                if (st["Name"]==name and st["Status"]=="Busy"):
                    jobac=job
                    job["Status"]= "Done"
                    st["Status"]= "NotReady"
                    job["Finished"]=1
                    st["QWating"]= st["QWating"]-job["Duration"]
                    break
    name=jobac["Stylist"]
    for job in Jobs: 
        if(job["ID"] != id and job["Status"]=="Assigned" and job["Stylist"]==name):
            print("#######",jobac["Duration"])
            job["QWating"]=job["QWating"]-jobac["Duration"]
            print(job["QWating"]) 
    with open(jsonFile, "w+") as f:
        json.dump(Jobs, f)
    f.close()
    with open(stylistjson, "w+") as f:
        json.dump(Stylists, f)
    f.close()
    print(jobac)     
    return jsonify(jobac)                


@app.route("/login/<int:id>", methods= ['GET'])
def login(id):
    for st in Stylists:
        if st["StylistID"] == id:  
            ipadd = request.environ['REMOTE_ADDR']
            st["IPAddr"]=ipadd
            st["Status"]="NotReady"           
            with open(stylistjson, "w+") as f:
                json.dump(Stylists, f)
            f.close()
            return jsonify(st)
    stfail={"Name": "Unknown"}
    print(stfail)
    return jsonify(stfail)
 
 
@app.route("/logoff/<name>", methods= ['GET'])
def logoff(name):
    for st in Stylists:
        if st["Name"] == name:  
            st["Status"]="Offline"
            with open(stylistjson, "w+") as f:
                json.dump(Stylists, f)
            f.close()
            return jsonify(st)   
    
    
@app.route("/stylists", methods=["GET"])
def get_stylists():    
    return make_response(jsonify(Stylists))


@app.route("/stylists/<int:id>", methods= ['GET'])
def get_stylist_by_id(id):
    for stylist in Stylists:
        if stylist["StylistID"] == id:  
            return jsonify(stylist)


@app.route("/stylists/jobs/<int:id>", methods = ['GET'])
def get_jobs_by_stylistID(id):
    name=""
    for stylist in Stylists:
        if stylist["StylistID"] == id:
            name = stylist["Name"];
            break;  
    stylistjobs=[]
    for job in Jobs:
        if job["Stylist"] == name:
            stylistjobs.append(job)
    return jsonify(stylistjobs)

    
@app.route("/login/<name>", methods= ['GET'])
def ready(name):
    for st in Stylists:
        if st["Name"] == name:  
            st["Status"]="Ready"
            with open(stylistjson, "w+") as f:
                json.dump(Stylists, f)
            f.close()
            print(st)
            return jsonify(st)      


@sock.route('/echo')
def echo(sock):
    while True:
        data = sock.receive()
        print("*****> "+data)
        sock.send(data)       

@sock.route('/job')
def job(sock):
    while True:
        id=int(sock.receive())
        for job in Jobs:
            if job["ID"] == id:  
                print(job)
                sock.send(job)
                break  

                
@sock.route('/stylist')
def stylist(sock):
    while True:
        stylist=sock.receive()
        print(stylist)
        for job in Jobs:
            if (job["Stylist"]==stylist and job["Status"]=="Assigned"):
                print(job)
                sock.send(job)
                break

             
if __name__ == "__main__":
    sock.run(app)


    

