from flask import Flask, request, render_template, url_for, session, redirect
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
app = Flask(__name__)
"""
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'gpacalc'


app.config['MYSQL_HOST'] = 'db4free.net'
app.config['MYSQL_USER'] = 'gpacalc'
app.config['MYSQL_PASSWORD'] = 'Candy@69'
app.config['MYSQL_DB'] = 'gpacalc'
"""
app.config['MYSQL_HOST'] = 'remotemysql.com'
app.config['MYSQL_USER'] = 'rVDdLPKZIw'
app.config['MYSQL_PASSWORD'] = 'MOCryJTHA9'
app.config['MYSQL_DB'] = 'rVDdLPKZIw'

mysql = MySQL(app)

app.secret_key ='jntuh'

@app.route('/')
def home():
    return render_template('index.html')

#--------------------------------------------------------------

@app.route('/register')
def register():
    return render_template('register.html')

#--------------------------------------------------------------

@app.route('/registerdata',methods=["POST","GET"])
def registerdata():
    if request.method == "POST":
        alert=""
        flag = 0
        name = request.form.get('name')
        name = name.title()
        email = request.form.get('email')
        password = request.form.get('password')
        rollno = request.form.get('rollno').upper()
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM USERS WHERE EMAIL = % s",(email,))
        user = cursor.fetchone()
        if(user):
            alert = "You're already a member with email '%s'"%(email)
            flag=1
        elif not re.match(r'[0-9]{2}[A-Za-z]{2}[0-9][A-Za-z]+0+[0-9][A-Za-z0-9][0-9]',rollno):
            alert = "Invalid JNTUH rollno '%s'"%(rollno)
            flag=1
        else:
            cursor.execute("INSERT INTO USERS VALUES(NULL,% s,% s,% s,% s)",(name,email,password,rollno))
            alert = "Congratulations!, Dear \"%s\" You've Successfully Registered."%(name)
            cursor.connection.commit()
        if(flag==1):
            indicator = "danger"
        else:
            indicator = "success"
        return render_template('register.html',alert=alert,indicator=indicator)
        
#--------------------------------------------------------------
     
@app.route('/termsandconditions')
def tnc():
    return render_template('termsandconditions.html')

#--------------------------------------------------------------

@app.route('/login')
def login():
    return render_template('login.html')
    
#--------------------------------------------------------------

@app.route('/loginauth',methods=["POST","GET"])
def loginauth():
    if request.method == "POST":
        alert=""
        flag = 0
        email = request.form.get('email')
        password = request.form.get('password')
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM USERS WHERE EMAIL = % s",(email,))
        acc = cursor.fetchone()
        if not acc:
            alert = "We couldn't find an account with this email address."
            return render_template('login.html',alert=alert,indicator="danger")
        else:
            cursor.execute("SELECT * FROM USERS WHERE EMAIL = % s AND PASSWORD = % s",(email,password))
            user = cursor.fetchone()
            cursor.connection.commit()
            if(user):
                session['loggedin'] = True
                session['id'] = user[0]
                session['name'] = user[1]
                session['email'] = user[2]
                session['rollno'] = user[4]
                return redirect(url_for('dashboard'))
            else:
                alert = "Incorrect Email and Password Combination"
                return render_template('login.html',alert=alert,indicator="danger")
    else:
        return render_template("login")

#--------------------------------------------------------------

@app.route('/dashboard')
def dashboardnew():
    if 'id' in session:
        uid = session['id']
        alert = ""
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM USERS WHERE UID = % s",(uid,))
        a = cursor.fetchone()
        if a:
            alert = "Welcome to JNTUH GPA Calc , %s "%(session['name'],)
            return render_template('home.html',alert=alert,cvisibility="block",adisplay="block",sgpas="",cgpa="",rollno=session['rollno'])
    else:
        return redirect(url_for('login'))

#--------------------------------------------------------------

@app.route('/home')
def dashboard():
    if 'id' in session:
        uid = session['id']
        alert = ""
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM GPARECORDS WHERE UID = % s",(uid,))
        a = cursor.fetchone()
        if not a:
            return redirect(url_for('dashboardnew'))
        else:
            account = list(a)
            cursor.connection.commit()
            count = 0
            for i in range(8):
                if account[i+3] != 0:
                    count = count + 1
            sum1 = sum(account[3:11])
            li = []
            for i in account:
                if i==0.0:
                    li.append("-")
                else:
                    li.append(i)
            cgpa = sum1/count
            cgpa = float("{0:.2f}".format(cgpa))    
            if count==8:
                cursor.execute("UPDATE GPARECORDS SET CGPA = % s WHERE UID = % s",(cgpa,uid,))
            cursor.connection.commit()
            return render_template('home.html',dvisibility="block",count=count,bdisplay="block",sgpas=li[3:],cgpa=cgpa,rollno="")
    else:
        return redirect(url_for('login'))

#--------------------------------------------------------------    

@app.route('/results')
def results():
    if 'id' in session:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM RESULTS")
        results = cursor.fetchall()
        cursor.connection.commit()
        return render_template('results.html',results=results)
    else:
        return redirect(url_for('login'))
#--------------------------------------------------------------

@app.route('/calc-gpa')
def calcgpa():
    if 'id' in session:
        return render_template('calc-gpa.html')
    else:
        return redirect(url_for('login'))

#--------------------------------------------------------------

@app.route('/fetch-subjects',methods=["POST","GET"])
def fetchsubjects():
    if 'id' in session and request.method == "POST":
        text = ""
        reg = int(request.form.get('reg'))
        branch = int(request.form.get('branch'))
        sem = int(request.form.get('sem'))
        session['reg'] = reg
        session['branch'] = branch
        session['sem'] = sem
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM SEMSUBJECTS WHERE SID = % s AND RID = % s",(sem,branch))
        results = cursor.fetchall()
        cursor.connection.commit()
        if sem==1:
            text="I Year - I Semester"
        elif(sem==2):
            text="I Year - II Semester"
        elif(sem==3):
            text="II Year - I Semester"
        elif(sem==4):
            text="II Year - II Semester"
        elif(sem==5):
            text="III Year - I Semester"
        elif(sem==6):
            text="III Year - II Semester"
        elif(sem==7):
            text="IV Year - I Semester"  
        elif(sem==8):
            text="IV Year - II Semester"   
        total = 0
        for i in results:
            total = total+i[4]
        return render_template('calc-gpa.html',results=results,total=total,semtitle=text,gpoints="",indicator="block")
    else:
        return redirect(url_for('login'))

#--------------------------------------------------------------

@app.route('/calculate',methods=["POST","GET"])
def calculate():
    if 'id' in session:
        uid = session['id']
        if request.method == "POST":
            text = ""
            alert = ""
            fail = 0
            cursor = mysql.connection.cursor()
            sem = session['sem']
            branch = session['branch']
            cursor.execute("SELECT * FROM SEMSUBJECTS WHERE SID = % s AND RID = % s",(sem,branch))
            results = list(cursor.fetchall())
            cursor.connection.commit()
            total = 0
            for i in results:
                total = total+i[4]
            gpoints = []
            
            for subject in results:
                string = "s"+str(subject[0])
                g = float(request.form[string])
                if(g==0.0):
                    fail = fail+1
                gp = float(subject[4]*g) 
                gpoints.append(gp)
            val = sum(gpoints)
            sgpa = val/total
            sgpa = float("{0:.2f}".format(sgpa))
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM GPARECORDS WHERE UID = % s",(uid,))
            account = cursor.fetchone()
            if not account:
                cursor.execute("INSERT INTO GPARECORDS VALUES(NULL,% s,% s,0,0,0,0,0,0,0,0,0)",(uid,branch))
            if account:
                if(branch != account[2]):
                    gpoints = []
                    alert = "Please make sure, 'branch' you've selected is correct !"
                    return render_template('calc-gpa.html',results=results,total=total,semtitle=text,gpoints=gpoints,indicator="block",alert=alert)
                else:
                    pass;                
            if sem==1:
                text="I Year - I Semester"
                cursor.execute("SELECT * FROM GPARECORDS WHERE ONE= % s AND UID = % s",(sgpa,uid,))
                acc = cursor.fetchone()
                if not acc:
                    cursor.execute("UPDATE GPARECORDS SET ONE = % s WHERE UID = % s",(sgpa,uid,))
            elif(sem==2):
                text="I Year - II Semester"
                cursor.execute("SELECT * FROM GPARECORDS WHERE TWO = % s AND UID = % s",(sgpa,uid,))
                acc = cursor.fetchone()
                if not acc:
                    cursor.execute("UPDATE GPARECORDS SET TWO = % s WHERE UID = % s",(sgpa,uid,))
            elif(sem==3):
                text="II Year - I Semester"
                cursor.execute("SELECT * FROM GPARECORDS WHERE THREE = % s AND UID = % s",(sgpa,uid,))
                acc = cursor.fetchone()
                if not acc:
                    cursor.execute("UPDATE GPARECORDS SET THREE  = % s WHERE UID = % s",(sgpa,uid,))
            elif(sem==4):
                text="II Year - II Semester"
                cursor.execute("SELECT * FROM GPARECORDS WHERE FOUR = % s AND UID = % s",(sgpa,uid,))
                acc = cursor.fetchone()
                if not acc:
                    cursor.execute("UPDATE GPARECORDS SET FOUR  = % s WHERE UID = % s",(sgpa,uid,))
            elif(sem==5):
                text="III Year - I Semester"
                cursor.execute("SELECT * FROM GPARECORDS WHERE FIVE = % s AND UID = % s",(sgpa,uid,))
                acc = cursor.fetchone()
                if not acc:
                    cursor.execute("UPDATE GPARECORDS SET FIVE = % s WHERE UID = % s",(sgpa,uid,))
            elif(sem==6):
                text="III Year - II Semester"
                cursor.execute("SELECT * FROM GPARECORDS WHERE SIX = % s AND UID = % s",(sgpa,uid,))
                acc = cursor.fetchone()
                if not acc:
                    cursor.execute("UPDATE GPARECORDS SET SIX = % s WHERE UID = % s",(sgpa,uid,))
            elif(sem==7):
                text="IV Year - I Semester"
                cursor.execute("SELECT * FROM GPARECORDS WHERE SEVEN = % s AND UID = % s",(sgpa,uid,))
                acc = cursor.fetchone()
                if not acc:
                    cursor.execute("UPDATE GPARECORDS SET SEVEN = % s WHERE UID = % s",(sgpa,uid,))
            elif(sem==8):
                text="IV Year - II Semester"
                cursor.execute("SELECT * FROM GPARECORDS WHERE EIGHT = % s AND UID = % s",(sgpa,uid,))
                acc = cursor.fetchone()
                if not acc:
                    cursor.execute("UPDATE GPARECORDS SET EIGHT = % s WHERE UID = % s",(sgpa,uid,))  
            cursor.connection.commit()
            if(fail):
                alert = "SGPA is calculated excluding % s failed Subjects"%(fail,)
                alertsuccess = "Be prepared for Exams ! All the Best :) !"
                return render_template('calc-gpa.html',results=results,total=total,semtitle=text,tvisibility="block",indicator="block",indi="block",sgpa=sgpa,gpoints=gpoints,gpvalue=val,alert=alert,alertsuccess=alertsuccess)
            return render_template('calc-gpa.html',results=results,total=total,semtitle=text,tvisibility="block",indicator="block",indi="block",sgpa=sgpa,gpoints=gpoints,gpvalue=val,alert=alert,alertsuccess="Congratulations !!")
    else:
        return redirect(url_for('login'))
#--------------------------------------------------------------

@app.route('/target-gpa-calc')
def gpaplanner():
    if 'id' in session:
        return render_template('target-gpa-calc.html')
    else:
        return redirect(url_for('login'))
#--------------------------------------------------------------

@app.route('/target-gpa',methods=["POST"])
def targetgpa():
    if 'id' in session:
        total = 8
        if request.method == "POST":
            gpa = float(request.form.get('gpa'))
            current = int(request.form.get('sem'))
            tgpa = float(request.form.get('tgpa'))  
            rem = int(total-(current-1))
            avggpa = ((tgpa*(rem+1))-gpa)/rem 
            avggpa = float("{0:.2f}".format(avggpa))
            txt="As you're fresher You can't get target-gpa..!"
            if(current==1):
                return render_template('target-gpa-calc.html',text=txt,indi="visible")
            else:
                return render_template('target-gpa-calc.html',avggpa=avggpa,tvisibility="block",rem=rem,indicator="visible")
    else:
        return redirect(url_for('login'))
#--------------------------------------------------------------

@app.route('/how-it-works')
def howitworks():
    return render_template('how-it-works.html')
   
 #-------------------------------------------------------------- 
   
@app.route('/logout')
def logout():
    if 'id' in session:
        session.pop('id',None)
        session.pop('email',None)
        session.pop('rollno',None)
        session.pop('name',None)
        return redirect(url_for('home'))
#--------------------------------------------------------------
if(__name__ == '__main__'):
    app.run(host="0.0.0.0",debug=True,port=8080)