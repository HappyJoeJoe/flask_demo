from app import db
from flask.ext.login import UserMixin

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