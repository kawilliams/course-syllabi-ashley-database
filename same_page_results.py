#!/usr/bin/python
import os
import logging
from flask import (Flask, request, flash, url_for, 
                   redirect, render_template, 
                   send_from_directory)
from werkzeug import secure_filename
from flask_sqlalchemy import SQLAlchemy


"""Decided to upload files to folder on server and store location in DB"""
UPLOAD_FOLDER = 'all_syllabi/'

app = Flask(__name__, template_folder = 'templates')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///FindCourses.sqlite3'
app.config['SECRET_KEY'] = 'secret'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

class Upload(db.Model):
    __tablename__ = 'uploads'
    id = db.Column('upload_id', db.Integer, primary_key = True)
    data = db.Column(db.String(40))
    desc = db.Column(db.String(250))    
    dept = db.Column(db.String(40))
    classnum = db.Column(db.String(10))
    year = db.Column(db.String(10))
    semester = db.Column(db.String(10))
    first_name = db.Column(db.String(40))
    last_name = db.Column(db.String(40))
    email = db.Column(db.String(40))
    visitable = db.Column(db.String(20))
    privacy = db.Column(db.String(10))

    
    
    def __init__(self, data, desc, dept, classnum, year, semester, 
                 first_name, last_name, email, visitable, privacy): 
        self.data = data
        self.desc = desc 
        self.dept = dept
        self.classnum = classnum
        self.year = year
        self.semester = semester
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.visitable = visitable
        self.privacy = privacy
        
       
@app.route('/')
@app.route('/show_all')
def show_all():
    courses = Upload.query.all()
    return render_template('show_all.html', uploads=courses)




@app.route('/get_courses', methods=['GET','POST'])
def get_courses():
    #logging.warning('get_courses method')
    if request.method == 'POST': 
        if request.form['submit'] == 'Enter':
            firstName = request.form['firstName'][0].upper() + request.form['firstName'][1:].lower()
            lastName = request.form['lastName'][0].upper() + request.form['lastName'][1:].lower()
            email = request.form['email'].lower
            
            if firstName == "":
                flash('Please enter your first name')
                return render_template('new_upload_table_Flaskfriendly.html', courses="", num_courses=0)
            if lastName == "":
                flash('Please enter your last name')
                return render_template('new_upload_table_Flaskfriendly.html', courses="", num_courses=0)
            if firstName != "" and lastName != "":
                return redirect(url_for('disp_courses', first_name=firstName, last_name=lastName))  
        if request.form['submit'] == 'Submit Syllabi':
            logging.warning('SUBMITTED!!!')
    
    return render_template('new_upload_table_Flaskfriendly.html', courses="", num_courses=0)






@app.route('/mycourses/<first_name>/<last_name>/', methods=['GET', 'POST'])
def disp_courses(first_name, last_name):
    #logging.warning("IN DISP COURSES!!") 
    #logging.warning(first_name)
    found = Upload.query.filter_by(last_name=last_name).filter_by(first_name=first_name).all()     
    #logging.warning(found) 
    if len(found) == 0:
        flash('No courses found. Please check your spelling and try again.')
    #for course in found:
        #course.first_name = first_name[0] + first_name[1:].lower()
        #course.last_name = last_name[0] + last_name[1:].lower()
        #logging.warning('FOund the courses')
        #render_template('new_upload_table_Flaskfriendly.html', courses=found)
        
    if request.method == 'POST':
        #logging.warning('something') 
        #logging.warning(request.form['submit'])
        #logging.warning(request.files['data0'].filename)
        
        ## get all changed fields
        for i in range(len(found)):
            found_id = found[i].id
            course_name = found[i].dept + ' ' + found[i].classnum
            
            #logging.warning(found_id)
            syl = "data"+str(i)
            vis = "visitable"+str(i)
            prv = "privacy"+str(i)
            
            new_syllabus = request.files[syl]
            new_visitable = request.form[vis]
            new_privacy = request.form[prv]
            
            if new_syllabus.filename == '':
                w = 'No selected file for ' + course_name
                flash(w)
                return redirect(request.url)
            
            #logging.warning(new_syllabus.filename)
            #logging.warning(new_visitable)
            #logging.warning(new_privacy)
            #logging.warning(found_id)
            
            filename = secure_filename(new_syllabus.filename)
            new_syllabus.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
          
            setattr(found[i], 'privacy', new_privacy)
            setattr(found[i], 'visitable', new_visitable)
            setattr(found[i], 'data', filename)
            
            db.session.commit()            
          
            
        return render_template('thankyou.html')
            
            
    return render_template('new_upload_table_Flaskfriendly.html', courses=found)



    
   
@app.route('/thankyou', methods=['GET','POST'])
def submit():
    logging.warning('submit method')    
    
    return render_template('thankyou.html')





@app.route('/syllabi/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/syllabi/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory=app.config['UPLOAD_FOLDER'], filename=filename)

if __name__ == "__main__":
    db.create_all()
    #course1 = Upload("course1file.tx", "description1", "CCC", "121", "2016", "F", 
                            #"Katy", "Williams", "kawilliams@davidson.edu", "Can visit", "All")
    #course2 = Upload("course2file.tx", "description2", "YKK", "221", "2016", "F", 
                            #"Katy", "Williams", "kawilliams@davidson.edu", "Can visit", "All")
    #course3 = Upload("course3file.tx", "description3", "XYZ", "321", "2016", "F", 
                            #"Keaton", "Williams", "kewilliams@davidson.edu", "Not open", "All")
    #course4 = Upload("course4file.tx", "description4", "MAT", "108", "2016", "F", 
                            #"Michael", "Mossinghoff", "mimossinghoff@davidson.edu", "Can visit", "All")
    #course5 = Upload("course5file.tx", "description5", "MAT", "110", "2016", "F", 
                            #"Donna", "Molinek", "domolinek@davidson.edu", "Can visit", "All")
  
    #db.session.add(course1)
    #db.session.add(course2)
    #db.session.add(course3)
    #db.session.add(course4)
    #db.session.add(course5)
    #db.session.commit()

    
    app.run(debug=True)