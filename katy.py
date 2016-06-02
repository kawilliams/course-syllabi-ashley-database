import os
import logging
from flask import (Flask, request, flash, url_for, 
                   redirect, render_template, 
                   send_from_directory)
from werkzeug import secure_filename
from flask_sqlalchemy import SQLAlchemy

"""Decided to upload files to folder on server and store location in DB"""
UPLOAD_FOLDER = 'syllabikt/'

app = Flask(__name__, template_folder = 'templates_katy')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///uploads.sqlite3'
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
def show_all():
    return render_template('show_all.html', uploads = Upload.query.all())

@app.route('/new', methods=['GET','POST'])
def new():
    logging.warning("katy")    
    if request.method == 'POST':
        
        filekt = request.files['data']
        desc = request.form['desc']
        dept = request.form['dept']
        classnum = request.form['classnum']
        year = request.form['year']
        semester = request.form['semester']
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        email = request.form['email']
        visitable = request.form['visitable']
        privacy = request.form['privacy']
        
        
        logging.warning(filekt.filename)
        logging.warning(email)
        logging.warning(visitable)
        logging.warning(privacy)
        
           
        if filekt.filename == '':
            flash('No selected file')
            return redirect(request.url)
        else:
            logging.warning("else")
            filename = secure_filename(filekt.filename)
            logging.warning(filename)
            logging.warning(os.path.join(app.config['UPLOAD_FOLDER']))
            logging.warning(filekt)
            filekt.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            location = url_for('uploaded_file', filename=filename)
            logging.warning(location)
            upload = Upload(filename, desc, dept, classnum, year, semester, 
                            first_name, last_name, email, visitable, privacy) 
            
            logging.warning("line 56")
            logging.warning(send_from_directory(app.config['UPLOAD_FOLDER'], filename))
            #return redirect(url_for('uploaded_file'), filename=filename)  
            
    
        db.session.add(upload)
        db.session.commit()
        flash('File added!')
        return redirect(url_for('show_all'))

    return render_template('new.html')

@app.route('/syllabi/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/syllabi/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory=app.config['UPLOAD_FOLDER'], filename=filename)

if __name__ == "__main__":
    db.create_all()
    #logging.warning("main")
    app.run(debug=True)