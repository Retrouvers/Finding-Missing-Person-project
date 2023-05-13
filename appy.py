from flask import Flask, flash, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import MySQLdb.cursors
import re
import os
import cv2
import numpy as np
import face_recognition


  
  
appy = Flask(__name__)

appy.config["IMAGE_UPLOADS"] = "C:/Users/hp/OneDrive/Desktop/Retrouver/static/user_images"
appy.config["IMAGE_UPLOADV"] = "C:/Users/hp/OneDrive/Desktop/Retrouver/static/victim_images"
appy.secret_key = 'xyzsdfg'
  
appy.config['MYSQL_HOST'] = 'localhost'
appy.config['MYSQL_USER'] = 'root'
appy.config['MYSQL_PASSWORD'] = ''
appy.config['MYSQL_DB'] = 'retrouver'
  
mysql = MySQL(appy)
  
@appy.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@appy.route('/login', methods =['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'uname' in request.form and 'password' in request.form:
        uname = request.form['uname']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE Username = % s AND Password = % s', (uname, password, ))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            
            session['username'] = uname
            mesage = 'Logged in successfully !'
            return redirect(url_for('victim'))
        else:
            mesage = 'Please enter correct username / password !'
    return render_template('login.html', mesage = mesage)
  


@appy.route('/register', methods=['GET', 'POST'])
def register():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form:
        username = request.form['name']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE Username = %s', (username,))
        account = cursor.fetchone()
        if account:
            mesage = 'Account already exists!'
        elif not username or not password:
            mesage = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO user VALUES (%s, %s, NULL, NULL, NULL, NULL, NULL, NULL)', (username, password))
            mysql.connection.commit()
            session['username'] = username # Store the username in the session
            return redirect(url_for('user')) # Redirect to the user.html template

    elif request.method == 'POST':
        mesage = 'Please fill out the form!'

    return render_template('register.html', mesage=mesage)


@appy.route('/user', methods=['GET', 'POST'])
def user():
    message = ''
    
    username = None
    if 'username' in session:
        username = session['username']
    if request.method == 'POST' and 'fname' in request.form and 'lname' in request.form:
                
        image = request.files['file']
        if image.filename == '':
            print("Filename is invalid")
            return redirect(request.url)
        username = session['username']
        basedir = os.path.abspath(os.path.dirname(__file__))
        filename = secure_filename(username + '.jpg') # Adding username to the filename and setting the extension to '.jpg'
        image.save(os.path.join(basedir, appy.config["IMAGE_UPLOADS"], filename))

        fname = request.form['fname']
        lname = request.form['lname']
        phone = request.form['phone']
        email = request.form['email']
        gender = request.form['gender']
        dob = request.form['dob']

        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE Username = %s', (username,))
        account = cursor.fetchone()
        if not lname or not fname or not phone or not email or not gender:
            message = 'Please fill out the form!'
        else:
            cursor.execute('UPDATE user SET User_fname = %s, User_lname = %s, User_gender = %s, User_contact = %s, User_DOB = %s, User_email = %s WHERE username = %s', (fname, lname, gender, phone, dob, email, username, ))

            mysql.connection.commit()
            message = 'You have created wuhuuu!'
            return redirect(url_for('victim'))

    elif request.method == 'POST':
        message = 'Please fill out the form!'
     
    return render_template('user.html', message=message, username=username)

@appy.route('/victim', methods=['GET', 'POST'])
def victim():
    message = ''
    filename = ''
    username = None
    if 'username' in session:
        username = session['username']
    idname=""    
    if request.method == 'POST' :
                
        image = request.files['file']
        if image.filename == '':
            print("Filename is invalid")
            return redirect(request.url)
        username = session['username']
        basedir = os.path.abspath(os.path.dirname(__file__))
        filename = secure_filename(username + '_'+image.filename) # Adding username to the filename and setting the extension to '.jpg'
        image.save(os.path.join(basedir, appy.config["IMAGE_UPLOADV"], filename))
        session['filename'] = filename
        
        fname = request.form['fname']
        lname = request.form['lname']
        # phone = request.form['phone']
        # email = request.form['email']
        gender = request.form['gender']
        dob = request.form['dob']
        path='static/user_images'
        images=[]
        classNames=[]
        myList=os.listdir(path)
        #print(myList)
        for cl in myList:
            curImg=cv2.imread(f'{path}/{cl}')
            images.append(curImg)
            classNames.append(os.path.splitext(cl)[0])
        #print(classNames)
        #print(images)


        def findEncodings(images):
        
            encodeList=[]
            for img in images:
                img=cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                faceEncodings = face_recognition.face_encodings(img)
                
                #print(faceEncodings)
                if len(faceEncodings) > 0:
                    encode= faceEncodings[0]
                    encodeList.append(encode) 
                
            return encodeList  
        encodeListKnown=findEncodings(images)
        #print("encoding completed")
        a="C:/Users/hp/OneDrive/Desktop/Retrouver/static/victim_images/"
        c=a+filename
        
        imgTest=cv2.imread(c)
        facelocTest= face_recognition.face_locations(imgTest)[0]
        encodeTest= face_recognition.face_encodings(imgTest)[0]


        matches=face_recognition.compare_faces(encodeListKnown,encodeTest)
        faceDis= face_recognition.face_distance(encodeListKnown,encodeTest)
        
        matchIndex=np.argmin(faceDis)
        
        if matches[matchIndex]:
            idname=classNames[matchIndex].upper()
            
            session['idname'] = idname
        else:
            message = 'No match found!'
            
            #return redirect(url_for('victim'))
            return render_template('victim.html', message=message)
            
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        if not lname or not fname or not gender:
            message = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO lost_person VALUES (%s, %s, %s, %s, %s)', (username, fname, lname, dob, gender, ))
            mysql.connection.commit()
            message = 'You have created wuhuuu!'
            return redirect(url_for('match'))


    elif request.method == 'POST':
        message = 'Please fill out the form!'
     
    return render_template('victim.html', message = message, username=username, filename=filename ,idname=idname)
    
  
@appy.route('/feedback', methods=['GET', 'POST'])
def feedback():
    message = ''
    
    username = None
    if 'username' in session:
        username = session['username']
    if request.method == 'POST' :
                
        
        username = session['username']
        
        feedback = request.form['feedback']
                
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE Username = %s', (username,))
        account = cursor.fetchone()
        if not feedback:
            message = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO feedback VALUES (%s, %s)', (username, feedback, ))

            mysql.connection.commit()
            message = 'You have created wuhuuu!'
            return redirect(url_for('victim'))

    elif request.method == 'POST':
        message = 'Please fill out the form!'
     
    return render_template('feedback.html', message=message, username=username)

@appy.route('/match', methods =['GET', 'POST'])
def match():
    mesage = ''
    filename = None
    idname = None
    fname = None
    lname = None
    dob = None
    email = None
    contact = None
    gender = None
    if 'idname' in session:
        idname = session['idname']
        
        
    if 'filename' in session:
        filename = session['filename']
         
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM user WHERE Username = % s', (idname, ))
    
    user = cursor.fetchone()
    if user:
        fname = user['User_fname']
        lname = user['User_lname']
        gender = user['User_gender']
        contact = user['User_contact']
        dob = user['User_DOB']
        email = user['User_email']
        
        return render_template('match.html', mesage=mesage, fname=fname, lname=lname, dob=dob, email=email, contact=contact, gender=gender, filename=filename, idname=idname)
    else:
        mesage = 'Please enter correct email / password !'
        
    match = request.form['match']
    if match == 'correct':
       return redirect(url_for('feedback'))
    elif match=='incorect' :
        return redirect(url_for('victim'))
    return render_template('match.html', mesage=mesage, fname=fname, lname=lname, dob=dob, email=email, contact=contact, gender=gender, filename=filename, idname=idname)

@appy.route('/logout')
def logout():
    # clear the session data
    session.clear()
    # redirect to the login page
    return redirect(url_for('login'))

@appy.route('/signup')
def signup():
    return render_template('register.html')

@appy.route('/display/<filename>')
def display_image(filename):
	return redirect(url_for('static',filename = "/user_images/" + filename), code=301)


    
if __name__ == "__main__":
    appy.run(debug=True,port=8000)
 
    