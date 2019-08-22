from app import db
from flask.ext.login import UserMixin

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
