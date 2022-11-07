from enum import Enum
from flask.globals import request
import mysql.connector ,json ,hashlib , re
from flask import Flask , Response , render_template,redirect, url_for, request, session, abort
from mysql.connector.errors import Error
from flask_httpauth import HTTPBasicAuth
from flask_login import LoginManager, UserMixin,login_required, login_user, logout_user
from sqlalchemy import null 

app = Flask(__name__)
auth = HTTPBasicAuth()
# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
app.config.update(
    SECRET_KEY = 'lkfjb2i9fghvskljrnq'
)

class User(UserMixin):

    def __init__(self, id):
        self.id = id

        
    def __repr__(self):
        return "%d" % (self.id)
# @auth.verify_password
# def verify_password(username, password):
#     mydb = mysql.connector.connect(
#             host="172.16.30.24",
#             user="remote_user",
#             password="S@b_DB_Pass_1",
#             database="dkmm"
#             )
#     mycursor = mydb.cursor()
#     mycursor.execute(f"select * from users where username = \'{str(username)}\'")
#     X = mycursor.fetchone()
#     mycursor.close()
#     mydb.close()
#     if X[2]== hashlib.md5(password.encode()).hexdigest():
#        return True

class contactDetailOperation(Enum):
    Delete = 1
    Update = 2
    Insert = 3


class Contacts:    
    def create(name,lastname): #Create a New Contact
        mydb = mysql.connector.connect(
            host="172.16.30.24",
            user="remote_user",
            password="S@b_DB_Pass_1",
            database="dkmm"
            )
        mycursor = mydb.cursor()
        try:
            mycursor.execute("insert into contacts (name , lastname) values (%s,%s) ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id)",(name,lastname))
        except Error as err: 
            if err.errno == 1062:
                return("duplicated")
        mydb.commit()
        the_lastrow = mycursor.lastrowid
        mycursor.close()
        mydb.close()
        return(the_lastrow)
    def showContactDetail(contactId): # Show All Contact details in DB
        mydb = mysql.connector.connect(
            host="172.16.30.24",
            user="remote_user",
            password="S@b_DB_Pass_1",
            database="dkmm"
            )
        mycursor = mydb.cursor()
        mycursor.execute(f"SELECT * FROM contact_details WHERE contact_id = {str(contactId)};")
        X = mycursor.fetchall()
        mycursor.close()
        mydb.close()
        # table = PrettyTable()
        # table.field_names = ["Type","Data","Contact_id"]
        # table.align["Data"]="l"
        output = []
        for i in X :
            output.append ({'type':i[1],'data':i[2]})
            # table.add_row([i[1],i[2],i[3]])
        # print(table)
        return(output)
    def showAllContacts(): # Show All Contacts in DB
        mydb = mysql.connector.connect(
            host="172.16.30.24",
            user="remote_user",
            password="S@b_DB_Pass_1",
            database="dkmm"
            )
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM contacts;")
        X = mycursor.fetchall()
        mycursor.close()
        mydb.close()
        output=[]
        for i in X :
            det = Contacts.showContactDetail(i[0])
            output.append({"contact":i,"detail":det})
        return(output)
    def updateContact(obj):
        mydb = mysql.connector.connect(
            host="172.16.30.24",
            user="remote_user",
            password="S@b_DB_Pass_1",
            database="dkmm"
            )
        mycursor = mydb.cursor()
        returnMsg = ''
        for detail in obj['contactDetail']:
            if 'operation' in detail :
                match contactDetailOperation(detail['operation']):
                    case contactDetailOperation.Update:
                        try :
                            mycursor.execute("UPDATE contact_details SET type=%s , data=%s , contact_id=%s where id=%s",(detail["type"],detail["data"],obj["contactId"],detail['detailId']))
                        except  Error as err:
                            returnMsg += f'Item : {detail} , error : {err}  |   ' 
                    case contactDetailOperation.Insert:
                        try:
                            mycursor.execute("insert into contact_details (type , data , contact_id) values (%s,%s,%s) ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id)",(detail["type"],detail["data"],obj["contactId"]))
                        except  Error as err:
                            returnMsg += f'Item : {detail} , error : {err}  |   ' 
                    case contactDetailOperation.Delete:
                        try:
                            mycursor.execute(f"DELETE FROM contact_details WHERE id = {detail['detailId']}")
                        except  Error as err:
                            returnMsg += f'Item : {detail} , error : {err}  |   ' 
            else: returnMsg += f"missing argumant Operation on detail :{detail}"
        mydb.commit()
        mycursor.close()
        mydb.close()
        # ContactDetail.createDetail(obj)
        return (returnMsg if returnMsg != '' else 'Job Done')
    def search (search):
        isLikeSearchStr = '%'+str(search['searchValue'])+'%'
        mydb = mysql.connector.connect(
            host="172.16.30.24",
            user="remote_user",
            password="S@b_DB_Pass_1",
            database="dkmm"
            )
        mycursor = mydb.cursor()
        match search['searchField']:
            case 'name':    
                query = f"SELECT * FROM contacts WHERE CONCAT(NAME,' ',lastname) LIKE '{isLikeSearchStr}'"
                mycursor.execute(query)
                X = mycursor.fetchall()
            case 'data':
                query = f"SELECT contacts.* FROM contact_details JOIN contacts ON  contact_details.`contact_id` = contacts.id WHERE data LIKE '{str(isLikeSearchStr)}'"
                mycursor.execute(query)
                X = mycursor.fetchall()

        mycursor.close()
        mydb.close()
        output = []
        for x in X:
            detail = Contacts.showContactDetail(x[0])
            output.append({"contact":x,"detail":detail})
            # print(x)
        return output
    def delete(cID):
        mydb = mysql.connector.connect(
            host="172.16.30.24",
            user="remote_user",
            password="S@b_DB_Pass_1",
            database="dkmm"
            )
        mycursor = mydb.cursor()
        query = (f"DELETE FROM contact_details WHERE contact_id = {str(cID)}")
        mycursor.execute(query)
        mycursor.execute(f"DELETE FROM contacts WHERE id = {str(cID)}")
        mydb.commit()
        mycursor.close()
        mydb.close()
        return(True)
class ContactDetail:
    def createDetail(inp): # Create
        mydb = mysql.connector.connect(
            host="172.16.30.24",
            user="remote_user",
            password="S@b_DB_Pass_1",
            database="dkmm"
            )
        mycursor = mydb.cursor()
        for i in inp["contactDetail"]:
            mycursor.execute("insert into contact_details (type , data , contact_id) values (%s,%s,%s) ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id)",(i["type"],i["data"],inp["contactId"]))
        mydb.commit()
        mycursor.close()
        mydb.close()
        output = Contacts.showContactDetail(inp["contactId"])
        return(output)
    
insert ={#              Sample Data Structure for Updating Contacts and Details
    "name":"Mehrdad",
    "lastname":"Moradabadi",
    "contactId":"1",
    "contactDetail":[{
        "detailId":"1",
        "type":"1",
        "data":"09128393976"},
        {"detailId":"2",
        "type":"1",
        "data":"09217154701"},
        {"detailId":"3",
        "type":"2",
        "data":"m.moradabadi@sabinarya.com"},
        {"type":"2",
        "data":"m.moradabadi@ssssssssabinarya.com"}
        ]}

@app.route('/add-contact',methods=['POST','GET'])
@login_required
def addContact ():
    if request.method=='POST':
        content = {'contactDetail':[]}
        contactName = request.form['name']
        contactlastname = request.form['lastname']
        index = 0
        for data in request.form.getlist('types[]'):
            content["contactDetail"].append({'type':data,'data':request.form.getlist('data[]')[index]})
            index += 1
        if contactName and contactlastname :
            cID = Contacts.create(contactName,contactlastname)
            content.update ({"contactId":cID})
            ContactDetail.createDetail(content)
        # r = Response()
        # r.headers["Content-Type"] = "application/json"
        # r.data =json.dumps({"data":"New Contact Created"})
            return (render_template('add-contact.html',status='success',message = 'contact saved'))
        else:
            return (render_template('add-contact.html',status='danger',message = 'contact not saved'))
    else :
        return (render_template('add-contact.html'))
@app.route('/',methods=['GET','POST'])
@login_required
def shAllContacts():
    output=Contacts.showAllContacts()   
    r = Response()
    r.headers["Content-Type"] = "application/json"
    if request.method == 'POST':
        if request.form and 'id' in request.form :
            Contacts.delete(request.form['id'])
        elif request.form and 'search' in request.form:
            searchObj = {}
            if re.match(r'^\d{0,11}$',request.form['search']) or re.match(r'^\w.*\@.*\..*$',request.form['search']):
                searchObj.update({"searchValue":request.form['search'],"searchField":"data"})
                output = Contacts.search(searchObj)
                return(render_template('index.html',value=output))
            else :
                searchObj.update({"searchValue":request.form['search'],"searchField":"name"})
                output = Contacts.search(searchObj)
                return(render_template('index.html',value=output))
    if output :
        r.data= json.dumps({"status":True,"result":output})
        r.status=200
    else : 
        r.data= json.dumps({"status":False,"result":"Error"})
        r.status=500
    return (render_template('index.html',value=output))
    # return Response(output,mimetypes='text/xml')
# @app.route('/searchcontacts',methods=['POST'])
# @login_required
# def searchContacts():
#     content = request.get_json()
#     r = Response()
#     r.headers["Content-Type"] = "application/json"
#     r.data =json.dumps({"status":True,"response":Contacts.search(content)})
#     return(r)
@app.route('/updatecontacts',methods=['POST'])
@login_required
def updateContacts():
    content = request.get_json()
    r = Response()
    r.headers["Content-Type"] = "application/json"
    r.data =json.dumps({"status":True,"response":Contacts.updateContact(content)})
    return(r)
@app.route('/deletecontacts',methods=['POST'])
@login_required
def deleteContacts():
    content = request.get_json()
    r = Response()
    r.headers["Content-Type"] = "application/json"
    r.data =json.dumps({"status":True,"response":Contacts.delete(content["cID"])})
    return(r)
# @app.route('/',methods=['GET'])
# def get_response():
#     out = "mehrdad"
#     return (render_template('index.html',value=out))
@app.route('/add-user',methods=['GET','POST'])
def new_user():
    if request.method == 'POST':
        username = request.form['username']
        passwd = request.form['password']
        mydb = mysql.connector.connect(
                host="172.16.30.24",
                user="remote_user",
                password="S@b_DB_Pass_1",
                database="dkmm"
                )
        password = hashlib.md5(passwd.encode()).hexdigest()
        mycursor = mydb.cursor()
        mycursor.execute("insert into users (username , password) values (%s,%s)", (username,password))
        mydb.commit()
        mycursor.close()
        mydb.close()
        return (render_template('add-user.html',status='success',message = 'New user created'))
    else : 
        mydb = mysql.connector.connect(
            host="172.16.30.24",
            user="remote_user",
            password="S@b_DB_Pass_1",
            database="dkmm"
                )
        mycursor = mydb.cursor()
        mycursor.execute("select * from users;")
        X = mycursor.fetchall()
        mycursor.close()
        mydb.close()
        output=[]
        for i in X :
            output.append({"users":i[1]})
        return(render_template('add-user.html',value = output))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  
        mydb = mysql.connector.connect(
            host="172.16.30.24",
            user="remote_user",
            password="S@b_DB_Pass_1",
            database="dkmm"
            )
        mycursor = mydb.cursor()
        mycursor.execute(f"select * from users where username = \'{str(username)}\'")
        X = mycursor.fetchone()
        mycursor.close()
        mydb.close()
              
        if X and X[2]== hashlib.md5(password.encode()).hexdigest():
                loginuser = User(username)
                login_user(loginuser)
                return redirect("/")
        else:
            return (render_template('login.html',value="Login failed try again"))
    else:
        return (render_template('login.html'))#Response('''
        #<form action="" method="post">
         #   <p><input type=text name=username>
          #  <p><input type=password name=password>
           # <p><input type=submit value=Login>
        #</form>
        #''')
# somewhere to logout
@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect("/")
# handle login failed
@app.errorhandler(404)
def page_not_found(e):
    return render_template('pagenotfound.html')
    
# callback to reload the user object        
@login_manager.user_loader
def load_user(userid):
    return User(userid)


if __name__=='__main__':
    app.run(host='0.0.0.0',port=5100,debug=True)