import os
import time
import  logging
from datetime import datetime
from flask_cors import CORS, cross_origin
import flask
import requests
from flask_bcrypt import  Bcrypt
from flask import Flask, request, render_template,session ,flash, redirect, url_for, jsonify
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user,current_user
import json
LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

UPLOAD_FOLDER = os.path.join(os.path.abspath(os.getcwd()),"static/video").replace('\\', '/')
#path = ('sqlite:///' + os.path.join(os.path.abspath(os.getcwd()), 'tmp/database.db')).replace('\\', '/')
#currentdurectory=os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
app.config['SECRET_KEY']='thissujuhdydtdggtdt'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mindful.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/mindfulrelax'

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
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100),  unique=True, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

class videomeditation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    iduser= db.Column(db.String(255), nullable=False)
    idvideo = db.Column(db.String(255), nullable=False)
    videourl = db.Column(db.String(255), nullable=False)
    namevideo = db.Column(db.String(255), nullable=True)
    datevideo = db.Column(db.String(255), nullable=True)

class videoresponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(255), nullable=False)
    video = db.Column(db.String(255), nullable=False)
    score_result=db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.String(255), nullable=True)
    physiology_score = db.Column(db.String(255), nullable=True)
    image = db.Column(db.String(255), nullable=True)
    videoanysis = db.Column(db.String(255), nullable=True)
    zip = db.Column(db.String(255), nullable=True)
    html = db.Column(db.String(255), nullable=True)
    json = db.Column(db.String(255), nullable=True)


class comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(100), nullable=False)
    datecreation = db.Column(db.String(100), nullable=False)
    namesender = db.Column(db.String(100), nullable=True)

db.create_all()
#sendvideo to the api
@app.route('/uploadandsend/', methods=["GET", "POST"])
@cross_origin()
def load():
    payLoad = dict()

    if request.method == "POST":
        file = request.files['attachment']
        filename = secure_filename(file.filename)
        try :
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        except:
            return jsonify('error', 'file not save')
        else:
            time.sleep(3)
            headers={}
            url = "http://mindfulrelax.ru/api/v1/meditation/video/create/"
            payload = {
                'name': filename,
                'meditation':1
                       }
           files = [('attachment',  (filename, open(UPLOAD_FOLDER + '/{}'.format(filename), 'rb'),'application/octet-stream'))]
            #check fille attachement
            if files:
                responsvideocreation = requests.request("POST", url, headers=headers, data=payload, files=files)
                print(files)
                print('succes1')
                time.sleep(3)
                if session['user'] is not None:
                    iduser = session['user']
                    data = responsvideocreation.json()
                    date=datetime.now()
                    savevideo = videomeditation(iduser=iduser, idvideo=data.get('id'), videourl=data.get('attachment'),
                                                namevideo=data.get('name'), datevideo=date)
                    db.session.add(savevideo)
                    db.session.commit()
                    #step  to send video for analyse

                    time.sleep(5)
                    url = "http://mindfulrelax.ru/api/v1/meditation/create/"

                    payload = { 'text' : '',
                                'created_at' : '',
                                'neural_network_score':'',
                                'physiology_score':'',
                                'wearble_device_score':'',
                                'user': 1,
                                'meditation_video': data.get('id')
                    }
                    headers = {}
                    time.sleep(2)
                    responsecreation = requests.request("POST", url, headers=headers, data=payload)
                    datacreation = responsecreation.json()
                    print('succes2 meditation creation')

                    # endstep  to send video for analyse
                    '''
                        get id meditation create
                    '''
                    # step  to get video analyse response
                    idmeditationcreted=datacreation.get('id')
                    '''
                        get check the meditation in default user
                    '''
                    savevideo = videoresponse(userid=session['user'],
                                              video=datacreation.get('id'),
                                              videoanysis=datacreation.get('id'),
                                              created_at=datetime.now(),
                                              )
                    db.session.add(savevideo)
                    db.session.commit()
                    return  redirect(url_for('home'))
                else:
                    #when user is not connected

                    return render_template('/')
            else:
                return redirect(url_for('home'))
                #print('ggdb')#response.json()


#let comment
@app.route('/comment/', methods=["GET", "POST"])
def comment():
    if request.method == 'POST':
        req = request.form
        data = req.get("comment")
        date= datetime.now()
        newdata = comments(message=data,datecreation=date)
        print(newdata)
        db.session.add(newdata)
        db.session.commit()
        return jsonify("status", "success")
#json.dumps({'success':True}), 200, {'ContentType':'application/json'}


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
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        newdata = Users(username=username, email=email, password=hashed_password)
        db.session.add(newdata)
        db.session.commit()
        return jsonify("status", "success")


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

@app.route("/updatetraitement/")
@login_required
def userupdattraitement():
    id_user=session['user']
    user = Users.query.filter_by(id=id_user).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        login = request.form['login']
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = Users(id= id_user, username=login, email=email, password=hashed_password)

        db.session.add(user)
        db.session.commit()


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
    session.pop("user",None)
    return redirect(url_for('home'))


#user vue
@app.route('/login/')
def login():
        return render_template('pages/login.html')
#user traitement
@app.route('/loginchecker/',methods=["GET", "POST"])
def logincheker():
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
                flask.flash('Logged in successfully.')
                return redirect(url_for("useraccount",user_id=user.id))
            else:
                flash('error data connexion.')
                return render_template('pages/login.html')
        else:
            return flash('error data connexion.')

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
            'valeur':'no data yet '
        }
        return render_template("admin/idmedite.html", datas=missing,user_id=session['user'],name=current_user.username,nbre=nombrevideo)

@app.route('/about/')
def about():
    return render_template('pages/about.html')

#call record video page
@app.route('/record/')
def record():
    return render_template('pages/record.html')

#home page
@app.route('/',defaults={'dataset': None})
def home(dataset):
    if dataset is None:
        return render_template('home.html')
    else:
        return render_template('home.html',dataAnalyse=dataset)


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')
