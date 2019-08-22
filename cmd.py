#!/usr/bin/env python
# encoding:utf-8

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sys

# 创建对象的基类:
Base = declarative_base()

# 定义User对象:
class User(Base):
	__tablename__ = 'account'

	id = Column(Integer, primary_key=True)
	name = Column(String(1024))
	telphone = Column(String(1024))
	mail = Column(String(1024))

	def __repr__(self):
		return "<%s name:%s telphone:%s mail:%s>" % (self.id, self.name, self.telphone, self.mail)

def main():
	for i in range(1, len(sys.argv)):
		print("arg[%s] :%s" % (i, sys.argv[i]))

	if(len(sys.argv) != 4):
		print("arg num wrong")

	engine = create_engine("mysql+pymysql://root:root@localhost:3306/example?charset=utf8")
	DBSession = sessionmaker(bind=engine)

	session = DBSession()
	new_user = User(name=sys.argv[1], telphone=sys.argv[2], mail=sys.argv[3])
	session.add(new_user)
	session.commit()
	session.close()

if __name__ == "__main__":
	main()