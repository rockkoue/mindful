import json
import os
import time
from datetime import datetime
import requests
from flask import Flask, request, render_template, session, redirect, url_for, jsonify, flash
from flask_bcrypt import Bcrypt
from flask_bootstrap import Bootstrap
from flask_cors import CORS, cross_origin
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename



UPLOAD_FOLDER = os.path.join(os.path.abspath(os.getcwd()),"static/video").replace('\\', '/')
#currentdurectory=os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
app.config['SECRET_KEY']='thissujuhdydtdggtdt'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost/mindfulrelax'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
bcrypt = Bcrypt(app)
class Users(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self,username,email,password):
        self.username=username
        self.email=email
        self.password=password

class videomeditation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    iduser= db.Column(db.String(255), nullable=False)
    idvideo = db.Column(db.String(255), nullable=False)
    videourl = db.Column(db.String(255), nullable=False)
    namevideo = db.Column(db.String(255), nullable=True)
    datevideo = db.Column(db.String(255), nullable=True)

    def __init__(self,iduser,idvideo,videourl,namevideo,datevideo):
        self.iduser=iduser
        self.idvideo = idvideo
        self.videourl=videourl
        self.namevideo=namevideo
        self.datevideo = datevideo

class videoresponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(255), nullable=True)
    video = db.Column(db.String(255), nullable=True)
    videoanysis=db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.String(255), nullable=True)


    def __init__(self, userid, video, videoanysis,created_at):
        self.userid = userid
        self.video = video
        self.videoanysis = videoanysis
        self.created_at = created_at




class comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(100), nullable=True)
    datecreation = db.Column(db.String(100), nullable=True)

    def __init__(self, message, datecreation):
        self.message = message
        self.datecreation = datecreation


db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))
#sendvideo to the api
@app.route('/', methods=["GET", "POST"])
@cross_origin()
def home():
    payLoad = dict()
    error = None
    if request.method == "POST":
       if "user" in session:
           file = request.files['attachment']
           filename = secure_filename(file.filename.replace(" ", ""))
           url = "http://mindfulrelax.ru/api/v1/meditation/video/all/"

           headers = {}
           payload = {}
           responseforattachement = requests.request("GET", url, headers=headers, data=payload).json()
           attachemeditation=len(responseforattachement)+1

           try:
               file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename.replace(" ", "")))
           except:
               return jsonify('error', 'file not save')
           else:
               headers = {}
               time.sleep(3)
               url = "http://mindfulrelax.ru/api/v1/meditation/video/create/"
               payload = {
                        'name': filename,
                        'meditation': attachemeditation
                            }
               print(filename)
               files = [('attachment',
                         (filename, open(UPLOAD_FOLDER + '/{}'.format(filename), 'rb'), 'application/octet-stream'))]
               if files:
                   responsvideocreation = requests.request("POST", url, headers=headers, data=payload, files=files)

                   time.sleep(3)

                   iduser = session['user']
                   data = responsvideocreation.json()
                   date = datetime.now()
                   savevideo = videomeditation(iduser=iduser, idvideo=data.get('id'),
                                               videourl=data.get('attachment'),
                                               namevideo=data.get('name'),
                                               datevideo=date)
                   db.session.add(savevideo)
                   db.session.commit()
                   # step  to send video for analyse
                   time.sleep(5)
                   url = "http://mindfulrelax.ru/api/v1/meditation/create/"
                   payload = {'text': '',
                              'created_at': '',
                              'neural_network_score': '',
                              'physiology_score': '',
                              'wearble_device_score': '',
                              'user': 1,
                              'meditation_video': data.get('id')
                              }
                   headers = {}
                   time.sleep(2)
                   responsecreation = requests.request("POST", url, headers=headers, data=payload)
                   datacreation = responsecreation.json()
                   savevideo = videoresponse(userid=session['user'],
                                             video=datacreation.get('id'),
                                             videoanysis=data.get('id'),
                                             created_at=datetime.now(),
                                             )
                   db.session.add(savevideo)
                   db.session.commit()
                   error = "uploaded with succes check you account "
               else:
                   error= "error file doawload"
       else:
           error =  "you can not upload video if you are not logged"
    return render_template('home.html',error=error)

#let comment
@app.route('/comment/', methods=["GET", "POST"])
def comment():
    if request.method == 'POST':
        req = request.form
        data = req.get("comment")
        date= datetime.now()
        newdata = comments(message=data,datecreation=date)
        db.session.add(newdata)
        db.session.commit()
        return jsonify("status", "success")


#vue register
@app.route('/register/',methods=["GET", "POST"])
def register():
    return render_template('pages/register.html')
#vue traitement
@app.route('/signinuser/',methods=["GET","POST"])
def signuser():
    if request.method == 'POST':
        req = request.form
        username = req.get("login")
        email = req.get("email")
        password = req.get("password")
        passwordcfi = req.get("passwordcfi")
        if(password != passwordcfi) :
            return jsonify(
                {"status" :"error","message":"password not identique"})
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            newdata = Users(username=username, email=email, password=hashed_password)
            db.session.add(newdata)
            db.session.commit()
            print(passwordcfi)
            return jsonify({"status": "success","message":"user created with success"})



@app.route("/profile/")
@login_required
def userprofil():
    id_user=session['user']
    user = Users.query.filter_by(id=id_user).first()
    return render_template('admin/profile.html',user_id=user)


@app.route("/update/")
@login_required
def userupdate():
    id_user=session['user']
    user = Users.query.filter_by(id=id_user).first()
    return render_template('admin/update.html',user_id=user)

@app.route("/updatetraitement",methods=['GET', 'POST'])
def userupdattraitement():
    id_user=session['user']
    if request.method =="POST":
        #user = Users.query.filter_by(id=id_user).first()
        user = Users.query.get_or_404(id_user)
        if user:
            user.username = request.form['login']
            user.email = request.form['email']
            mdp = request.form['password']
            user.password = bcrypt.generate_password_hash(mdp).decode('utf-8')
            try:
                db.session.commit()
                flash("user  uppdated")
                redirect(url_for('userupdate'))
            except:
                flash("error  uppdated")
                redirect(url_for('userupdate'))
    return render_template('admin/update.html',user_id=user)



#get a user info meditation
@app.route('/users/<int:user_id>')
@login_required
def useraccount(user_id):
    userconnect=str(session['user'])
    nombrevideo=videomeditation.query.filter(videomeditation.iduser.endswith(userconnect)).all()
    responsevideo = videoresponse.query.filter(videoresponse.userid.endswith(userconnect)).all()
    return render_template('admin/meditations.html', datas=responsevideo,name=current_user.username,user_id=session['user'],nbre=nombrevideo)


@app.route("/listevideo/")
@login_required
def mesvideo():
    userconnect = str(session['user'])
    nombrevideo = videomeditation.query.filter(videomeditation.iduser.endswith(userconnect)).all()
    return render_template('admin/listevideo.html',nbre=nombrevideo,user_id=userconnect)

@app.errorhandler(404)
def page_not_found(error):
    return render_template("pages/404.html"), 404

#disconnexion
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop("user", None)
    return redirect(url_for('home'))
#user vue

#user traitement
@app.route('/login/',methods=["GET", "POST"])
def login():
    error=None
    if request.method == 'POST':
        req = request.form
        username = req.get("login")
        user = Users.query.filter_by(username=username).first()
        password=req.get("password")
        if user:
            user_id = user.id
            session['user'] = user_id

            if bcrypt.check_password_hash(user.password,password):
                login_user(user)
                return redirect(url_for("useraccount",user_id=user.id))
            else:
                error="error password"
        else:
             error= "User not found"

    return render_template('pages/login.html',error=error)

@app.route("/showcomment/")
def showcomment():
    liste = comments.query.all()
    return render_template("pages/comments.html",commentaire=liste)

@app.route("/idmeditation/<int:id>")
@login_required
def uniquemeditation(id):
    userconnect = str(session['user'])
    nombrevideo = videomeditation.query.filter(videomeditation.iduser.endswith(userconnect)).all()
    responsevideo = videoresponse.query.filter(videoresponse.userid.endswith(userconnect)).all()
    headers={}
    url = f"http://mindfulrelax.ru/api/v1/meditation/update/{id}"
    listedata=[]
    response = requests.request("GET", url, headers=headers)
    resultat = response.json()
    if resultat['video_analysis'] !='waiting' :
        try:
            if isinstance(resultat['video_analysis'], str):
                videoAnalyseDict = json.loads(resultat['video_analysis'].replace('\'', '"'))
            else:
                videoAnalyseDict = {}
        except json.JSONDecodeError as exc:
            # LOG.debug(f'Exc {exc}', exc_info=True)
            videoAnalyseDict = {}

        listedata.append({
            'score': resultat['score_result'],
            'meditation_video': str(resultat['meditation_video']),
            'image': videoAnalyseDict.get('image'),
            'video': videoAnalyseDict.get('video'),
            'json': videoAnalyseDict.get('json'),
            'zip': videoAnalyseDict.get('zip'),
            'html': videoAnalyseDict.get('html')
        })
        listedatas=[]
        for item in listedata:
            listedatas= item
        return render_template("admin/idmedite.html",data=listedatas,user_id=session['user'],name=current_user.username,nbre=nombrevideo)
    else:
        missing={
            'valeur':'no data yet the algorithm is working on video wait few minute'
        }
        return render_template("admin/idmedite.html", datas=missing,user_id=session['user'],name=current_user.username,nbre=nombrevideo)

@app.route('/about')
def about():
    return render_template('pages/about.html')

#call record video page
@app.route('/record')
def record():
    return render_template('pages/record.html')



if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')
