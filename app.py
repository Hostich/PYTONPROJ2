import sys
sys.path.insert(0,"db/")
from db.dbhelper import *
import qrcode
import io 
import os

from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, Response, session, jsonify,send_file


upload_folder="static/images"
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = upload_folder
app.secret_key = "a1c11254bb08151a46ecf2744dba5961"
qrcode_folder = "static/qrcode"


@app.route('/qrcode')
def generateqr():
    idno = request.args.get('idno', '')
    if not idno:
        return send_file('static/qrcode/placeholder.png', mimetype='image/png')

    qr_path = f'static/qrcode/{idno}.png'
    if os.path.exists(qr_path):
        return send_file(qr_path, mimetype='image/png')

    # Generate new QR if not exists
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(idno)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(qr_path)
    return send_file(qr_path, mimetype='image/png')
    
@app.route("/")
def index()->None:
    return render_template("index.html")

@app.route("/login")
def login()->None:
    return render_template("adminlogin.html")
 
@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect("/")
    
@app.route("/admin")
def admin()->None:
    school:list = getall('admin')
    return render_template("admin.html", adminlist = school)
  
@app.route("/student")
def student()->None:
    school:list = getall('students')
    return render_template("studentmgt.html", studentslist = school, student=None)
    
@app.route("/addstudent")
def addstudent()->None:
    return render_template("student.html")

@app.route("/getstudent")
def getstudent():
    idno = request.args.get('idno')
    lastname = request.args.get('lastname')
    if not idno:
        return "No ID number provided", 400

  
    student_list = getrecord('students', idno=idno)
    if not student_list:
        flash('Student Not Found', 'error')
        return redirect("/")

    student = dict(student_list[0])
   
   
    image_path = f'images/{student["lastname"]}.png' 
    if not os.path.exists(os.path.join(app.static_folder, image_path)):
        image_path = 'images/account.png'
    
    
    student['image'] = url_for('static', filename=f'images/{student["lastname"]}.png')

    return render_template('check.html', student=student)


@app.route("/loginvalidate", methods=["POST"])
def loginvalidate()->None:
    email:str = request.form.get('email')
    password:str = request.form.get('password')
    school:list = getrecord('admin', email=email, password=password)
    if len(school) > 0:
        session['email'] = email
        return redirect("/admin")
    else:
        flash('incorect email or password','error')
        return redirect("/login")

@app.route("/deletestudent")
def deletestudent()->None:
    id:int = request.args.get('id')
    ok:bool = deleterecord('students',id=id)
    if ok==True:
        flash("Student Deleted","success")
    else:
        flash("Error Deleting Student","error")
    return redirect(url_for("student"))    
        
@app.route("/deleteadmin")
def deleteadmin()->None:
    id:int = request.args.get('id')
    ok:bool = deleterecord('admin',id=id)
    if ok==True:
        flash("Admin Deleted","success")
    else:
        flash("Error Deleting Admin","error")
    return redirect(url_for("admin"))


@app.route("/saveadmin", methods=['POST'])
def saveadmin()->None:
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    id = request.form.get('id')
    action_type = request.form.get('type')

    if action_type == 'add':
        ok = addrecord('admin', name=name, email=email, password=password)
        if ok:
            flash("Admin added successfully!", "success")
    elif action_type == 'edit':
        ok = updaterecord('admin', id=id, name=name, email=email, password=password)
        if ok:
            flash("Admin updated successfully!", "success")
    else:
        flash("Invalid action type", "error")

    return redirect(url_for('admin'))
    
@app.route("/savestudent",methods=['POST','GET'])
def savestudent()->None:
    if request.method=="POST":
        file:any = request.files['webcam']
        idno:str = request.form.get('idno') or request.args.get('idno')
        lastname:str = request.form.get('lastname') or request.args.get('lastname')
        firstname:str = request.form.get('firstname') or request.args.get('firstname')
        course:str = request.form.get('course') or request.args.get('course')
        level:str = request.form.get('level') or request.args.get('level')
        id = request.form.get('id') or request.args.get('id')
        type = request.form.get('type') or request.args.get('type')
        filename = upload_folder+"/"+lastname+".png"
        file.save(filename)
        
        if not all([idno, lastname, firstname, course, level, file]):
            flash("All fields and photo must be filled!", "error")
            return redirect("/student")
        
        if type == 'add':
            ok = addrecord(
                'students',
                idno=idno, lastname=lastname, firstname=firstname,
                course=course, level=level, image=filename
            )

        elif type == 'edit':
            ok = updaterecord(
                'students',
                id=id, idno=idno, lastname=lastname,
                firstname=firstname, course=course,
                level=level, image=filename
            )

        else:
            flash("Invalid action type", "error")
            return redirect(url_for('index'))

        flash("Student information saved successfully" if ok else "Error saving student",
              "success" if ok else "error")
              
        
        flash("Student information saved successfully" if ok else "Error saving student", "success" if ok else "error")
        
    return redirect(url_for('index'))

@app.route("/addstudents")
def addstudents():
    student_id = request.args.get("id")
    idno = request.args.get("idno", "")
    lastname = request.args.get("lastname", "")
    firstname = request.args.get("firstname", "")
    course = request.args.get("course", "")
    level = request.args.get("level", "")
    
    student = None
    if student_id: 
        student = {
            'id': student_id,
            'idno': idno,
            'lastname': lastname,
            'firstname': firstname,
            'course': course,
            'level': level,
            'image': f"images/{lastname}.png" 
        }

    return render_template("student.html",
                           student_id=student_id,
                           idno=idno,
                           lastname=lastname,
                           firstname=firstname,
                           course=course,
                           level=level)
                           
@app.route("/attendance")
def attendance()->None:
    return render_template("viewattendance.html")
    
@app.route("/attendance_update")
def attendance_update()->None:
    date_str = request.args.get("date")
    if not date_str:
        return jsonify([]) 

    records = getrecord("attendance", date=date_str)
    return jsonify(records)

@app.route("/record", methods=["POST"])
def record():
    idno = request.form.get("idno")

    if not idno:
        flash("No ID provided", "error")
        return redirect(url_for("index"))

    student_list = getrecord("students", idno=idno)
    if not student_list:
        flash("Student not found", "error")
        return redirect(url_for("index"))

    student = student_list[0]
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    time_in = datetime.now().strftime("%H:%M:%S")

    existing = getrecord("attendance", idno=idno, date=date_str)
    if existing:
        flash("Attendance already recorded", "error")
        return redirect(url_for("index"))

    addrecord(
        "attendance",
        idno=idno,
        lastname=student["lastname"],
        firstname=student["firstname"],
        course=student["course"],
        level=student["level"],
        date=date_str,
        time_in=time_in
    )

    return redirect(url_for("getstudent", idno=idno))


        
if __name__=="__main__":
	app.run(debug=True,host='0.0.0.0')