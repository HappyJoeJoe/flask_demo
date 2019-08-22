# encoding: utf-8
import pymysql
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify,Flask,render_template,redirect,make_response,session,request
from flask_login import UserMixin,LoginManager,login_user,login_required,current_user,logout_user
from wtforms import StringField,BooleanField,HiddenField,TextAreaField,DateTimeField,SubmitField
from wtforms.validators import DataRequired,Length
from flask_wtf.form import FlaskForm
from PIL import Image, ImageFont, ImageDraw, ImageFilter
from io import BytesIO
import random
import traceback
import json
from flask_mail import Mail, Message
import re
import urllib
import urllib2
import requests

app = Flask(__name__)

app.config["SECRET_KEY"] = "12345678"

#配置flask配置对象中键：SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:root@localhost:3306/example?charset=utf8"

#配置flask配置对象中键：SQLALCHEMY_COMMIT_TEARDOWN,设置为True,应用会自动在每次请求结束后提交数据库中变动
app.config['SQLALCHEMY_COMMIT_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

app.config['MAIL_SERVER'] = 'smtp.exmail.qq.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'jiabo.zhou@lixinchuxing.com'
app.config['MAIL_PASSWORD'] = 'xxxx'

app.config['FLASKY_MAIL_SENDER'] = 'jiabo.zhou@lixinchuxing.com'  # this is sender
app.config['FLASKY_ADMIN'] = 'jiabo.zhou@lixinchuxing.com'  # this is the email of admin
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'  # this is subject of email we will send

mailbox=Mail(app)
#获取SQLAlchemy实例对象，接下来就可以使用对象调用数据
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

# 加载用户的回调函数
@login_manager.user_loader
def load_user(user_id):
    print('call load_user')
    return User.query.get(user_id)

class User(UserMixin,db.Model):
	__tablename__ = 'account'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(1024), unique=True, nullable=False)
	telphone = db.Column(db.String(1024), unique=True, nullable=False)
	mail = db.Column(db.String(1024), unique=True, nullable=False)

	def __init__(self, name, telphone, mail):
		self.name = name
		self.telphone = telphone
		self.mail = mail

	def __repr__(self):
		return '<{},{},{}, {}>'.format(self.id, self.name, self.telphone, self.mail)

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return self.id

	@staticmethod
	def add_user(name, telphone, mail):
		user = User(name, telphone, mail)
		db.session.add(user)
		db.session.commit()

	@staticmethod
	def query_user(id):
		return User.query.get(id)

	@staticmethod
	def query_user_by_name(name):
		return User.query.filter_by(name=name).first()

	@staticmethod
	def query_user_by_tel(telphone):
		return User.query.filter_by(telphone=telphone).first()

	@staticmethod
	def query_user_by_mail(mail):
		return User.query.filter_by(mail=mail).first()

class Comment(db.Model):
	__tablename__ = 'comments'
	id = db.Column(db.BigInteger, primary_key=True)
	account_id = db.Column(db.BigInteger, unique=True, nullable=False)
	comment = db.Column(db.String(80), unique=True, nullable=False)
	status = db.Column(db.SmallInteger, unique=True, nullable=False)
	create_time = db.Column(db.DateTime, unique=False, nullable=False)

	def __init__(self, account_id, comment):
		self.account_id = account_id
		self.comment = comment
		self.status = 0

	def __repr__(self):
		return '<{} {}>'.format(self.comment, self.create_time)

	@staticmethod
	def delete_one(id):
		comment = Comment.query.get(id)
		db.session.delete(comment)
		db.session.commit()

	@staticmethod
	def add_one(comment):
		db.session.add(comment)
		db.session.commit()

	@staticmethod
	def update_one(comment):
		db.session.add(comment)
		db.session.commit()

	@staticmethod
	def query_one(id):
		return Comment.query.get(id)

	@staticmethod
	def query_all():
		return Comment.query.all()

class MyMessage():
	def __init__(self, id, account_id, comment, create_time):
		self.id = id
		self.account_id = account_id
		self.content = comment
		self.created_at = create_time
		

def validate_picture():
	total = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ012345789'
	# 图片大小130 x 50
	width = 130
	heighth = 50
	# 先生成一个新图片对象
	im = Image.new('RGB',(width, heighth), 'green')
	# 设置字体
	font = ImageFont.truetype('FreeSans', 40)
	# 创建draw对象
	draw = ImageDraw.Draw(im)
	str = ''
	# 输出每一个文字
	for item in range(5):
		text = random.choice(total)
		str += text
		draw.text((5+random.randint(4,7)+20*item,5+random.randint(3,7)), text=text, fill='black',font=font )

	# 模糊下,加个帅帅的滤镜～
	im = im.filter(ImageFilter.FIND_EDGES)
	return im, str

@app.route('/v1/verification-code', methods=['POST'])
def get_code():
	total = '012345789'
	str = ''
	for item in range(5):
		text = random.choice(total)
		str += text
	
	data = request.get_data()
	data = json.loads(data)
	mobile = data['mobile']
	captcha = data['captcha']

	mail = ''
	match = re.match('^[A-Za-z\d]+([-_.][A-Za-z\d]+)*@([A-Za-z\d]+[-.])+[A-Za-z\d]{2,4}$', mobile)
	if match:
		mail = match.group()
		msg = Message('Hello', sender = app.config['FLASKY_MAIL_SENDER'], recipients=[mail])
		msg.body = "您的验证码是: " + str
		mailbox.send(msg)
		session['sms'] = str
		return jsonify({'code': 0, 'message': '验证码已发送至邮箱'})

	session['sms'] = str
	print("mobile:%s  image:%s  sms:%s"%(mobile, session['image'], str))
	return jsonify({'code': 0, 'message': 'code:'+str})

@app.route('/v1/captcha', methods=['GET', 'POST'])
def get_captcha():
	image, str = validate_picture()
	# 将验证码图片以二进制形式写入在内存中，防止将图片都放在文件夹中，占用大量磁盘
	buf = BytesIO()
	image.save(buf, 'jpeg')
	buf_str = buf.getvalue()
	response = make_response(buf_str)
	response.headers['Content-Type'] = 'image/gif'
	session['image'] = str
	print("image =======> :%s"%(str))
	return response

class MyLoginForm(FlaskForm):
	name = StringField('name')
	mobile = StringField('mobile')
	captcha = StringField('captcha')
	verification_code = StringField('verification_code')

class MessageForm(FlaskForm):
	message = StringField('create-message-form',validators=[DataRequired(message=u"评论不能为空"),Length(1,1024,message=u'长度位于1~1024之间')],render_kw={'placeholder':u'输入评论'})

@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect("/login")

@app.route("/login", methods=['GET', 'POST'])
def login():
	if request.method == "GET":
		code = request.args.get("code")
		if code != None:

			access_token = ""
			url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=ww58a4328331200e28&corpsecret=lPEKHhgIikxWafeSJwnXaJHi6R0uAa-ZEtr-Sdpyw3o"
			r = requests.get(url, verify=False)
			try:
				dic_source = json.loads(r.text)
				access_token = dic_source['access_token']
			except:
				print(r.text)

			url = "https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo?access_token=" + access_token + "&code=" + code
			r = requests.get(url, verify=False)
			try:
				dic_source = json.loads(r.text)
				UserId = dic_source['UserId']
				user = User.query_user_by_name(UserId)
				if user == None:
					User.add_user(UserId, "", "")
					user = User.query_user_by_name(UserId)
				login_user(user)
				return redirect('/messages')
			except:
				print(r.text)
				return "登录失败"

		form = MyLoginForm()
		
		return render_template("pages/login.html",form=form)
	else:
		form = MyLoginForm()
		if form.validate_on_submit():
			name = form.name.data
			mobile = form.mobile.data
			captcha = form.captcha.data
			verification_code = form.verification_code.data

			print("mobile:%s  image:  %s  sms: %s"%(mobile, session['image'], session['sms']))
			if captcha != session['image'] or verification_code != session['sms']:
				return "登录失败"

			user = User.query_user_by_name(name)
			if user != None:
				return "昵称重复"

			match = re.match('^[A-Za-z\d]+([-_.][A-Za-z\d]+)*@([A-Za-z\d]+[-.])+[A-Za-z\d]{2,4}$', mobile)
			if match:
				mail = match.group()
				user = User.query_user_by_mail(mail)
				if user == None:
					User.add_user(name, "", mail)
				user = User.query_user_by_mail(mail)
			else:
				user = User.query_user_by_tel(mobile)
				if user == None:
					User.add_user(name, mobile, "")
				user = User.query_user_by_tel(mobile)

			login_user(user)
			return redirect('/messages')
		else:
			return "登录失败"

@app.route("/messages", methods=['GET', 'POST', 'DELETE'])
@login_required
def messages():
	if request.method == "GET" or request.method == "DELETE":
		form = MessageForm()
	else:
		form = MessageForm()
		message = form.message.data
		form.message.data = ""
		one = Comment(current_user.id, message)
		Comment.add_one(one)

	messages = []
	tmp = Comment.query_all()
	for one in tmp:
		messages.append(MyMessage(one.id, one.account_id, one.comment, one.create_time))
	return render_template('pages/messages.html', form=form, user=current_user, messages=messages)

@app.route("/v1/messages/<int:id>", methods=['DELETE'])
@login_required
def delete_message(id):
	form = MessageForm()
	Comment.delete_one(id)
	return redirect('/messages')

@app.route("/messages/<int:message_id>", methods=['POST', 'GET'])
@login_required
def update_message(message_id):
	form = MessageForm()
	comment = Comment.query_one(message_id)
	comment.comment = form.message.data
	Comment.update_one(comment)
	return redirect('/messages')

if __name__ == "__main__":
    app.run(debug = True)