# from flask import Flask,redirect,render_template,request,url_for,flash
# import json
# from flask_sqlalchemy import SQLAlchemy
# import pypyodbc as odbc
from flask_mail import Mail, Message
from flask import Flask,redirect,render_template,request,url_for,flash
from flask_sqlalchemy import SQLAlchemy
import pyodbc
from flask import Flask,redirect,render_template,request,url_for,flash,jsonify
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.inspection import inspect
from flask.globals import session
from flask import flash
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,login_manager,UserMixin,LoginManager,login_required,logout_user
from flask_login import current_user
from flask_mail import Mail
from werkzeug.utils import secure_filename
import os
from datetime import datetime 

local_server= True
app = Flask(__name__)
app.secret_key="^%$^$^^*&&FGGY9178"
 
login_manager=LoginManager(app)
login_manager.login_view='login'

with open('config.json','r') as c:
    params=json.load(c)["params"]

#
#  mail configuraton


app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password']
)
mail = Mail(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://tap2023:tap2023@APINP-ELPTYIXVW\SQLEXPRESS/crudApp?driver=SQL Server'
db = SQLAlchemy(app)
# DRIVER_NAME='SQL SERVER'
# SERVER_NAME='APINP-ELPTTQSW3\SQLEXPRESS'
# DATABASE_NAME='crudApp'
 
 
# connnection_string=connection_string = (
#     'DRIVER={SQL Server};'
#     'SERVER=APINP-ELPTTQSW3\SQLEXPRESS;'
#     'DATABASE=crudApp;'
#     'UID=tap2023;'
#     'PWD=tap2023;'
# )
# conn=odbc.connect(connnection_string)
# print(conn)
 
 
 
# local_server= True
# app=Flask(__name__)
# app.secret_key="^%$^$^^*&&FGGY9178"
 
 
# database configuration
# app.config['SQLALCHEMY_DATABASE_URI']='mysql://username:password@localhost/databasename'
# app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/flaskcrudapp'
# db=SQLAlchemy(app)
 
@login_manager.user_loader
def load_user(user_id):
    return Signup.query.get(user_id)


 
 
# configuration of database tables
class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(15))

class Signup(UserMixin,db.Model):
    user_id=db.Column(db.Integer,primary_key=True)
    first_name=db.Column(db.String(50))
    last_name=db.Column(db.String(50))
    email=db.Column(db.String(100),unique=True)
    password=db.Column(db.String(1000))
    phone=db.Column(db.String(12),unique=True)
    
    def get_id(self):
        return self.user_id

class Products(db.Model):
    pid=db.Column(db.Integer,primary_key=True)
    productName=db.Column(db.String(50))
    productDescription=db.Column(db.String(100))
    rating=db.Column(db.Integer)
    stocks=db.Column(db.Integer)
    price=db.Column(db.Integer)
 
@app.route("/test/")
def test():
    try:
        # query=Test.query.all()
        # print(query)
        sql_query="Select * from test"
        with db.engine.begin() as conn:
            response=conn.exec_driver_sql(sql_query).all()
            print(response)
        return f"Database is connected"
 
    except Exception as e:
        return f"Database is not connected {e} "
 
 
@app.route("/")
def home():
    products=Products.query.all()
    return render_template("index.html",products=products)

@app.route("/signup",methods=['GET','POST'])
def signup():
    try:
        if request.method=="POST":
            firstName=request.form.get("fname")
            lastName=request.form.get("lname")
            email=request.form.get("email")
            phone=request.form.get("phone")
            pass1=request.form.get("pass1")
            pass2=request.form.get("pass2")

            if pass1!=pass2:
                flash("Password is not matching","warning")
                return redirect(url_for("signup"))
            
            fetchemail=Signup.query.filter_by(email=email).first()
            fetchphone=Signup.query.filter_by(phone=phone).first()

            if fetchemail or fetchphone:
                flash("User Already Exists","info")
                return redirect(url_for("signup"))

            if len(phone)!=10:
                flash("Please Enter 10 digit number","primary")
                return redirect(url_for("signup"))
            
            gen_pass=generate_password_hash(pass1)
            query=f"INSERT into `signup` (`first_name`,`last_name`,`email`,`password`,`phone`) VALUES ('{firstName}','{lastName}','{email}','{gen_pass}','{phone}')"

            with db.engine.begin() as conn:
                conn.exec_driver_sql(query)               
               # my mail starts from here if you not need to send mail comment the below line           
                # mail.send_message('Signup Success',sender=params["gmail-user"],recipients=[email],body="Welcome to my website" )
                flash("Signup is Successs Please Login","success")
                return redirect(url_for("login"))

        return render_template("signup.html")
    except Exception as e:
        return f"Database is not connected {e} "
    
@app.route("/login",methods=['GET','POST'])
def login():
    try:
        if request.method=="POST":
            email=request.form.get('email')
            password=request.form.get('pass1')
            user=Signup.query.filter_by(email=email).first()
            if user and check_password_hash(user.password,password):
                login_user(user)
                flash("Login Success","success")
                return redirect(url_for("home"))
            else:
                flash("Invalid Credentials","warning")
                return redirect(url_for("login"))


        return render_template("login.html")
    except Exception as e:
        return f"Database is not connected {e} "
    


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout Success","primary")
    return redirect(url_for("login"))

# create operation
@app.route("/create",methods=['GET','POST'])
def create():
    if request.method=="POST":
        pName=request.form.get('productname')
        pDesc=request.form.get('productDesc')
        pRating=request.form.get('rating')
        pStocks=request.form.get('stocks')
        pPrice=request.form.get('price')
        # query=Products(productName=pName,productDescription=pDesc,rating=pRating,stocks=pStocks,price=pPrice)
        # db.session.add(query)
        # db.session.commit()
        sql_query=f"INSERT INTO [products] ([productName], [productDescription], [rating], [stocks], [price]) VALUES ('{pName}', '{pDesc}', '{pRating}', '{pStocks}', '{pPrice}')"
        with db.engine.begin() as conn:
            conn.exec_driver_sql(sql_query)
            flash("Product is Added Successfully","success")
            return redirect(url_for('home'))
       
 
 
    return render_template("index.html")
 
# update operation
@app.route("/update/<int:id>",methods=['GET','POST'])
def update(id):
    product=Products.query.filter_by(pid=id).first()
    if request.method=="POST":
        pName=request.form.get('productname')
        pDesc=request.form.get('productDesc')
        pRating=request.form.get('rating')
        pStocks=request.form.get('stocks')
        pPrice=request.form.get('price')
        # query=Products(productName=pName,productDescription=pDesc,rating=pRating,stocks=pStocks,price=pPrice)
        # db.session.add(query)
        # db.session.commit()
        sql_query=f"UPDATE [products] SET [productName]='{pName}',[productDescription]='{pDesc}',[rating]='{pRating}',[stocks]='{pStocks}',[price]='{pPrice}' WHERE [pid]='{id}'"
       
        with db.engine.begin() as conn:
            conn.exec_driver_sql(sql_query)
            flash("Product is Updated Successfully","primary")
            return redirect(url_for('home'))
 
 
    return render_template("edit.html",product=product)
 
 
 
# delete operation
@app.route("/delete/<int:id>",methods=['GET'])
def delete(id):
    # print(id)
    query=f"DELETE FROM [products] WHERE [pid]={id}"
    with db.engine.begin() as conn:
        conn.exec_driver_sql(query)
        flash("Product Deleted Successfully","danger")
        return redirect(url_for('home'))
   
@app.route("/search", methods=['POST'])
def search():
    search = request.form.get('search')
    # check if the input string can be converted to an integer
    if search.isdigit():
        products = Products.query.filter_by(pid=int(search)).all()
    else:
        products = Products.query.filter(Products.productName.like("%"+search+"%")).all()
 
    return render_template("index.html", products=products)
 
@app.route("/contact")
def contact():
    return render_template("contact.html")
   
app.run(debug=True)