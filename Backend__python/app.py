from flask import Flask, render_template,redirect,request,jsonify,session

from flask_pymongo import PyMongo
import jwt
from functools import wraps

#from flask_security import login_required
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
#from flask_login import LoginManager
app = Flask(__name__)
SECRET_KEY = "64456676#$$%dge"
#login_manager = LoginManager()
#login_manager.init_app(app)
app.config['SECRET_KEY'] = SECRET_KEY

jwt = JWTManager(app)

app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
mongo = PyMongo(app)








def token_required(func):
    @wraps(func)
    def decorated(*args,**kwargs):
        token = request.args.get('token')

        if not token:
            return jsonify({'message': 'Token is missing!'})
        
        try:

            payload = jwt.decode(token ,app.config['SECRET_KEY'])

        except:
            return jsonify({'message':'Invalid Token!'})
    return decorated

@app.route('/' ,methods =['GET','POST'])
def register():
    
    if request.method =='POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']

        user = mongo.db.users.find_one({'username':username})
        if user:
            return redirect('/')
        
        mongo.db.users.insert_one({'username':username ,'password':password,'user_type':user_type})
        return redirect('/login')
   
    return render_template("register.html")


@app.route('/login',methods = ['GET' ,'POST'])
def login():
    if request.method== 'POST':
        username =request.form['username']
        password = request.form['password']
        session['username'] = username
        
        test_user = mongo.db.users.find_one({'username':username ,'password':password})
        
        if test_user:
            
            access_token = create_access_token(identity= username ,fresh= True )
            if access_token:
                mongo.db.users.update_one({'username':username},{'$set':{'access_token':access_token}})
            
            session['logged_in'] = True
            session['username'] = username
            
            
            return redirect('/dashboard')
        

        else:
            return redirect('/')
    
    return render_template('login.html')
    
@app.route('/dashboard')
def dashboard():
    username = session['username']
    user = mongo.db.users.find_one({'username':username})
    if user['user_type'] =='MEMBER':
    
        total_books = mongo.db.books.find()
        return render_template('ALLBOOK.html',total_books  = total_books ,username  = username)
    else:

        return render_template('librarian.html')
    

        
        

@app.route('/addBook' ,methods =['GET','POST'])
def addBook():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        isgn = request.form['isbn']
        quantity = request.form['quantity']

        mongo.db.books.insert_one({'title':title,'author':author,'isgn':isgn,'quantity':quantity,'status':'available'})

        
    allbooks = mongo.db.books.find()
    return render_template('book.html',allbooks = allbooks)

@app.route('/deleteB/<string:isgn>/')
def deleteB(isgn):

    mongo.db.books.delete_one({'isgn':isgn})

    return redirect('/addBook')

@app.route('/updateB/<string:isgn>/', methods = ['POST','GET'])
def updateB(isgn):
    if request.method =='POST':
        title = request.form['title']
        author = request.form['author']
        quantity = request.form['quantity']
        mongo.db.books.update_one({'isgn':isgn},{ '$set':{'title':title,'author':author ,'quantity':quantity}})
        return redirect('/addBook')
    book= mongo.db.books.find_one({'isgn':isgn})
    return render_template('update.html',book =book)


@app.route('/addUser',methods =['GET','POST'])

def addUser():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        mongo.db.users.insert_one({'username':username,'password':password,'user_type':'MEMBER'})

    
    allUser = mongo.db.users.find()

    return render_template('adduser.html',allUser = allUser)

@app.route('/deleteUser/<string:username>/')
def deleteUser(username):
    mongo.db.users.delete_one({'username': username})

    return redirect('/addUser')

@app.route('/updateUser/<string:username>/',methods =['GET','POST'])
def updateUser(username):

    if request.method =='POST':
        uname = request.form['username']
        mongo.db.users.update_one({'username':username},{'$set':{'username':uname}})

        return redirect('/addUser')
    
    user = mongo.db.users.find_one({'username':username})
    return render_template('updateUser.html',user = user)


@app.route('/borrow/<string:isgn>/')

def borrow(isgn):
    book = mongo.db.books.find_one({'isgn':isgn,'status':'available'})

    if book:
        mongo.db.books.update_one({'isgn':isgn},{
            '$set':{'status':'borrow'}
        })

    return redirect('/dashboard')


@app.route('/returnB/<string:isgn>/')
def returnB(isgn):
    book = mongo.db.books.find_one({'isgn':isgn ,'status':'borrow'})
    if book:
        mongo.db.books.update_one({'isgn':isgn},{'$set':{'status':'available'}})
    
    return redirect('/dashboard')

@app.route('/delete_account/<string:username>/')
def delete_account(username):
    mongo.db.users.delete_one({'username':username})

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)