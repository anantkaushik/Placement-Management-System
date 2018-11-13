from flask import Flask, render_template, redirect, url_for, request, g, session, send_file
import sqlite3 as sql,os,csv

app=Flask(__name__)
app.config["CACHE_TYPE"] = "null"
app.secret_key = os.urandom(24)

@app.route("/login_server", methods=["POST"])
def login_server():
   if request.method == "POST":
      enrollmentno = request.form['enrollmentno']
      password = request.form['password']
      print(len(enrollmentno),enrollmentno,password)
      con = sql.connect("static/test.db")
      cur = con.cursor()
      try:
         if len(enrollmentno) == 11:
            cur.execute("select password from student where enrollmentno = ?",(enrollmentno,))
            a = cur.fetchone();
            ta=str(a)
            output=ta[2:-3]
            print(output)
            cur.execute("select name from student where enrollmentno = ?",(enrollmentno,))
            b = cur.fetchone();
            cur.close()
            con.close()
            tb=str(b)
            name=tb[2:-3]
            print(output, name)
            session.pop('user', None)
            if request.form['password'] == output and output != '':
               session['user'] = name
               session['enr'] = enrollmentno
               return redirect("/student")
            return render_template("index.html",login_modal=True)
         else:
            cur.execute("select password from coordinator where teacherid = ?",(enrollmentno,))
            a = cur.fetchone();
            ta=str(a)
            output=ta[2:-3]
            cur.execute("select name from coordinator where teacherid = ?",(enrollmentno,))
            b = cur.fetchone();
            cur.close()
            con.close()
            tb=str(b)
            name=tb[2:-3]
            print(output, name)
            session.pop('user', None)
            if request.form['password'] == output and output != '':
               session['user'] = name
               session['enr'] = enrollmentno
               return redirect("/coordinator")
            return render_template("index.html",login_modal=True)
      except:
         return render_template("index.html",login_modal=True)


@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
      g.user = session['user']


@app.route('/logout')
def logout():
  session.pop('user', None)
  session.pop('enr', None)
  return redirect('/')

@app.route("/")
def index():
	return render_template("index.html")

@app.route('/about')
def about():
   return render_template("about.html")

@app.route('/recruiters')
def recruiters():
   con = sql.connect("static/test.db")
   cur = con.cursor()
   cur.execute("select companyid,name,cdetails,roleoffered,eligibility,location,salary,other,responsibility,image from company")
   inf = cur.fetchall()
   inf = [i for i in inf]
   for i in inf:
      for j in i:
         print(j)
      print()
   cur.close()
   con.close()
   return render_template("recruiters.html",result=inf)

@app.route('/events')
def events():
   con = sql.connect("static/test.db")
   cur = con.cursor()
   cur.execute("DELETE from event where date < (select date('now'))")
   cur.execute("select companyname,role,date,salary,venue,sno,salary,interviewprocess,other,link,dater from event ORDER BY date")
   inf = cur.fetchall()
   inf = [i for i in inf]
   for i in inf:
      for j in i:
         print(j)
      print()
   cur.close()
   con.close()
   return render_template("events.html",result=inf)

@app.route('/contact')
def contact():
   return render_template("contact.html")

@app.route('/coordinator')
def coordinator():
   if 'user' in session:
      con = sql.connect("static/test.db")
      cur = con.cursor()
      cur.execute("select email from coordinator where teacherid = ?",(session['enr'],))
      a = cur.fetchone();
      ta=str(a)
      output=ta[2:-3]
      cur.close()
      con.close()
      return render_template("coordinator.html",un=(session['user']).title(),eid=output)
   return redirect("/")

@app.route('/getlist', methods=["POST"])
def getlist():
   if 'user' in session:
      listType = request.form['listof']
      con = sql.connect("static/test.db")
      cur = con.cursor()
      cur.execute('select enrollmentno,name,batch,course,section,email,percent12,percent10,college,backlogs from student where interested = ?',(listType,))
      inf = cur.fetchall()
      with open('student.csv', 'w', newline='') as f_handle:
         writer = csv.writer(f_handle)
         # Add the header/column names
         header = ['Enrollment No','Name','Batch','Course','Section','Email Id','12th Percentage','10th Percentage','College Percentage','No. of Backlogs']
         writer.writerow(header)
         # Iterate over `data`  and  write to the csv file
         for row in inf:
            writer.writerow(row)
      cur.close()
      con.close()
   return send_file('student.csv', mimetype='text/csv', attachment_filename='student.csv', as_attachment=True)

@app.route('/createlist', methods=["POST"])
def createlist():
   if 'user' in session:
      college = request.form['college']
      backlogs = request.form['backlogs']
      percent12 = request.form['percent12']
      percent10 = request.form['percent10']
      con = sql.connect("static/test.db")
      cur = con.cursor()
      cur.execute('select enrollmentno,name,batch,course,section,email,percent12,percent10,college,backlogs from student where college >= ? and backlogs <= ? and percent12 >= ? and percent10 >= ?',(college,backlogs,percent12,percent10,))
      inf = cur.fetchall()
      with open('student.csv', 'w', newline='') as f_handle:
         writer = csv.writer(f_handle)
         # Add the header/column names
         header = ['Enrollment No','Name','Batch','Course','Section','Email Id','12th Percentage','10th Percentage','College Percentage','No. of Backlogs']
         writer.writerow(header)
         # Iterate over `data`  and  write to the csv file
         for row in inf:
            writer.writerow(row)
      cur.close()
      con.close()
   return send_file('student.csv', mimetype='text/csv', attachment_filename='student.csv', as_attachment=True)

@app.route('/student')
def student():
   if 'user' in session:
      con = sql.connect("static/test.db")
      cur = con.cursor()
      cur.execute("select name,enrollmentno,course,section,contactno,email,batch,percent12,dob,college,backlogs,py12,percent10,py10,careerobjective,maths,stream,areaofinterest,addons,interested from student where enrollmentno = ?",(session['enr'],))
      inf = cur.fetchall()
      inf = [j for i in inf for j in i]
      print("********",inf[14])
      cur.close()
      con.close()
      return render_template("student.html",un=(session['user']).title(),info=inf)
   return redirect("/")


@app.route('/studentf', methods=["POST"])
def studentf():
   if 'user' in session:
      if request.method == "POST":
         dob = request.form['dob']
         college = request.form['college']
         backlogs = request.form['backlogs']
         percent12 = request.form['percent12']
         py12 = request.form['py12']
         stream = request.form['stream']
         maths = request.form['maths']
         percent10 = request.form['percent10']
         py10 = request.form['py10']
         careerobjective = request.form['careerobjective']
         placement = request.form['placement']
         areaofinterest = request.form['areaofinterest']
         addons = request.form['addons']
         con = sql.connect("static/test.db")
         cur = con.cursor()
         cur.execute("update student set dob = ?,college = ?, backlogs = ?, percent12 = ?, py12 = ?, percent10 = ?, py10 = ?, stream = ?, maths = ?, careerobjective = ?, interested = ?, areaofinterest = ?, addons = ? WHERE enrollmentno = ?",(dob,college,backlogs,percent12,py12,percent10,py10,stream,maths,careerobjective,placement,areaofinterest,addons,session['enr']))
         con.commit()
         cur.close()
         con.close()
      return redirect("/student")
   return redirect("/")

@app.route('/createevent', methods=["POST"])
def createevent():
   if 'user' in session:
      if request.method == "POST":
         cname = request.form['cname']
         role = request.form['role']
         salary = request.form['salary']
         eligibility = request.form['eligibility']
         interviewprocess = request.form['interviewprocess']
         date = request.form['date']
         venue = request.form['venue']
         other = request.form['other']
         link = request.form['link']
         dater = request.form['dater']
         con = sql.connect("static/test.db")
         cur = con.cursor()
         cur.execute("INSERT INTO event(companyname,role, date , salary , venue, interviewprocess, other, link, dater) VALUES(?,?,?,?,?,?,?,?,?)",(cname,role,date,salary,venue,interviewprocess,other,link,dater))
         con.commit()
         cur.close()
         con.close()
      return redirect("/coordinator")
   return redirect("/")

@app.route("/cmessage", methods=["POST"])
def cmessage():
   if request.method == "POST":
      name = request.form['name']
      enrollno = int(request.form['enrollno'])
      email = request.form['email']
      subject = request.form['subject']
      message = request.form['message']
      con = sql.connect("static/test.db")
      cur = con.cursor()
      cur.execute("INSERT INTO contact(name,enrollment,email,subject,message)VALUES (?,?,?,?,?)",(name,enrollno,email,subject,message))
      print(name,enrollno,email,subject,message)
      con.commit()
      cur.close()
      con.close()
      return render_template("contact.html",c_modal=True)

@app.route('/changepass', methods=["POST"])
def changepass():
   if 'user' in session:
      if request.method == "POST":
         cpass = request.form['cpass']
         newpass = request.form['newpass']
         con = sql.connect("static/test.db")
         cur = con.cursor()
         cur.execute("select password from student where enrollmentno = ?",(session['enr'],))
         a = cur.fetchone();
         ta=str(a)
         output=ta[2:-3]
         if output == cpass and output != "":
            cur.execute("update student set password = ? WHERE enrollmentno = ?",(newpass,session['enr']))
         con.commit()
         cur.close()
         con.close()
      return redirect("/student")
   return redirect("/")

@app.route('/changepasst', methods=["POST"])
def changepasst():
   if 'user' in session:
      if request.method == "POST":
         cpass = request.form['cpass']
         newpass = request.form['newpass']
         con = sql.connect("static/test.db")
         cur = con.cursor()
         cur.execute("select password from coordinator where teacherid = ?",(session['enr'],))
         a = cur.fetchone();
         ta=str(a)
         output=ta[2:-3]
         print(output)
         if output == cpass and output != "":
            cur.execute("update coordinator set password = ? WHERE teacherid = ?",(newpass,session['enr']))
         con.commit()
         cur.close()
         con.close()
      return redirect("/coordinator")
   return redirect("/")
if __name__=="__main__":
	app.run(debug=True,port=5000)
