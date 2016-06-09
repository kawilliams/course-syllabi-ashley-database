#!/usr/bin/python
import os
import logging
from flask import (Flask, request, flash, url_for, 
                   redirect, render_template,
                   send_from_directory)
from werkzeug import secure_filename
from flask_sqlalchemy import SQLAlchemy

""" 
Have muliple forms on one page and not lose your mind.
This is version 1. It's done, no problems (knock on wood), but the
database is going to change so a few tweaks need to be made
before productionizing.
"""

UPLOAD_FOLDER = 'all_syllabi/'

app = Flask(__name__, template_folder = 'templates')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///CoursesHermon.sqlite3'
app.config['SECRET_KEY'] = 'secret'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


db = SQLAlchemy(app)

class Course(db.Model):
    __tablename__ = 'uploads'
    id = db.Column(db.Integer, primary_key = True) #computer generated
    title = db.Column(db.String(100)) #name of course
    dep = db.Column(db.String(100)) #department
    course_num = db.Column(db.Integer) #three digit (usually) course number
    class_time = db.Column(db.String(100)) 
    class_section = db.Column(db.String(100), default='0')
    class_place = db.Column(db.String(100)) #classroom
    class_days = db.Column(db.String(100)) 
    instructor = db.Column(db.String(100)) 
    acad_period = db.Column(db.String(100)) #semester and year
    course_attrib = db.Column(db.String(100)) #distribution requirements
    CRN = db.Column(db.Integer) #five digit CRN
    data = db.Column(db.String(100)) #link for syllabus file
    visitable = db.Column(db.String(20))
    privacy = db.Column(db.String(10))    
        
   
    
    def __init__(self, title, dep, course_num, class_time, 
                 class_section, class_place, class_days, instructor, 
                 acad_period, course_attrib, CRN, data, visitable, privacy): 
     
        self.title = title 
        self.dep = dep 
        self.course_num = course_num
        self.class_time = class_time
        self.class_section = class_section
        self.class_place = class_place
        self.class_days = class_days
        self.instructor = instructor
        self.acad_period = acad_period
        self.course_attrib = course_attrib
        self.CRN = CRN
        self.data = data #syllabus
        self.visitable = visitable
        self.privacy = privacy
@app.route('/', methods=['GET','POST'])        
def index():
    courses = Course.query.all()
    return render_template('show_all.html', courses=courses)

        
@app.route('/my_courses', methods=['GET','POST']) #decorator
def get_courses():
    if request.method == 'POST':
        if request.form['submit'] == 'Find My Courses':
            first = request.form['firstname']
            last = request.form['lastname']
            
            if first == "":
                flash('Please enter your first name')
                return render_template('revamp2.html', firstname="", 
                                       lastname="", courses="")
            if last == "":
                flash('Please enter your last name')
                return render_template('revamp2.html', firstname="", 
                                       lastname="", courses="")
            
            first_name = first[0].upper() + first[1:].lower()
            last_name = last[0].upper() + last[1:].lower()
            email = request.form['email'].lower
            
            db_name = last_name + ', ' + first_name[0]
            found = Course.query.filter_by(instructor=db_name).all()

            return render_template('revamp2.html', firstname=first_name, 
                                   lastname=last_name,courses=found,first_load=False)
                            
        if request.form['submit'] == 'Submit Syllabi':
            first = request.form['firstname']
            last = request.form['lastname']
            
            first_name = first[0].upper() + first[1:].lower()
            last_name = last[0].upper() + last[1:].lower()
            email = request.form['email'].lower
            
            db_name = last_name + ', ' + first_name[0]            
                       
            found = Course.query.filter_by(instructor=db_name).all()
            
            changed_syl_list = []
            changed_vis_list = []
            changed_prv_list = []
            
            for i in range(len(found)):
                
                course_name = (found[i].dep + ' ' + str(found[i].course_num) +
                               ': ' + found[i].title)
                
                #logging.warning(found_id)
                syl = "data"+str(i)
                vis = "visitable"+str(i)
                prv = "privacy"+str(i)
                
                new_syllabus = request.files[syl]
                new_visitable = request.form[vis]
                new_privacy = request.form[prv]
                
                filename = secure_filename(new_syllabus.filename)
                
                syl_changed = False
                vis_changed = False
                prv_changed = False
                logging.warning(new_syllabus.filename)
                logging.warning(filename)
                logging.warning(found[i].data)
                
                if len(filename) > 0 and new_syllabus.filename != found[i].data:
                    syl_changed = True
                    changed_syl_list.append(course_name)
                if new_visitable != found[i].visitable:
                    vis_changed = True
                    changed_vis_list.append(course_name)
                if new_privacy != found[i].privacy:
                    prv_changed = True
                    changed_prv_list.append(course_name)
                    
                if new_syllabus.filename != '':
                    #w = 'No selected file for ' + course_name
                    #flash(w)
                    #return redirect(request.url)
                
                    new_syllabus.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    setattr(found[i], 'data', filename)
              
                setattr(found[i], 'privacy', new_privacy)
                setattr(found[i], 'visitable', new_visitable)
                
                
                db.session.commit()       
                
            return render_template('thankyou.html', syl_list=changed_syl_list, 
                                   vis_list=changed_vis_list, 
                                   prv_list=changed_prv_list, first_load=False)
    
   
    return render_template('revamp2.html')



@app.route('/syllabi/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/syllabi/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    if filename != "":        
        uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
        return send_from_directory(directory=app.config['UPLOAD_FOLDER'], filename=filename)
    else:
        return ""



if __name__ == "__main__":
    
    db.create_all()
    
    #course1 = Course("Intro to Web Design", "CSC", 231, "0930-1020", "A", 
                     #"CHAM 1111", "M W F", "Staff, S", "201501", "MQRQ", 
                     #12345, "syllabus1.txt", "Can visit", "All")
    #course2 = Course("Summer 101: Beach", "SUM", 101, "0130-0220", "0", 
                     #"LAKE 1000", "M W F", "Guard, L", "201501", "SSRQ", 
                     #90210, "syllabus2.txt", "Can visit", "All")    
    #course3 = Course("Intro to Web Design", "CSC", 231, "1030-1120", "B", 
                     #"CHAM 1111", "M W F", "Staff, S", "201501", "MQRQ", 
                     #12346, "syllabus1.txt", "Can visit", "All")
    #course4 = Course("Very Long Class", "SLO", 399, "0140-0420", "0", 
                     #"CHAM 2121", "T R", "Guard, L", "201501", "VPRQ", 
                     #99999, "syllabus3.txt", "Not open", "Davidson")
    #course5 = Course("Netflix: Social Impact", "SOC", 331, "0815-0930", "0", 
                     #"SLOAN 100", "T R", "Vision, T", "201501", "SSRQ", 
                     #10101, "syllabus4.txt", "Not open", "All")
  
    #db.session.add(course1)
    #db.session.add(course2)
    #db.session.add(course3)
    #db.session.add(course4)
    #db.session.add(course5)
    
    #course6 = Course("Water Exercise", "AQU", 234, "0645-0800", "0", 
                     #"BAKER 100", "MTWRF", "Graham, J", "201501", "PERQ", 
                     #11189, "", "Not open", "All")
    #db.session.add(course6)
    #db.session.commit()    
    
    app.run(debug=True)
    app.secret_key = 'secret'