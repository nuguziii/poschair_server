import datetime
import sqlite3
from flask import Flask
from flask import redirect
from flask import request
from flask import session
from flask import url_for, abort, render_template, flash
#from data_generator import data
from functools import wraps



# create a flask application - this ``app`` object will be used to handle
# inbound requests, routing them to the proper 'view' functions, etc
app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/image/',methods=['GET','POST'])
def getImage():
        return redirect(url_for('static',filename='posture_sample.png'))


@app.route('/login/', methods=['GET', 'POST'])
def login():
	if request.method == 'POST' and request.form['email']:
		conn = sqlite3.connect("../POSCHAIR.db")
		c = conn.cursor()

		iemail = request.form['email']
		ipwd = request.form['pwd']

		c.execute("SELECT ID, pwd FROM USER WHERE ID = ?", (iemail,))
		k = c.fetchone()[0]

		try:
			if k[0] == iemail and k[1] == ipwd:
				return 'fetch success'
		except:
			return 'fetch failed'
	return 'success'


@app.route('/signup/', methods=['GET', 'POST'])
def signup():
	if request.method == 'POST':
		conn = sqlite3.connect("../POSCHAIR.db")
		c = conn.cursor()
		input = [request.form['email'], request.form['name'], request.form['pwd']]
		c.execute("INSERT INTO User(ID, name, pwd) VALUES (?,?,?)", input)

		return 'success'
		
	return render_template('./index.html')

	
'''
@app.route('/addInfo/', methods=['GET', 'POST'])
def addInfo():
	#age, sex, height, weight
	if request.method == 'POST':
		
	return render_template('./index.html')
'''

@app.route('/posture/', methods=['GET', 'POST'])
def getLabel():
	#label string으로 반환한다
	if request.method == 'GET':
		return 'success'
		

if __name__=='__main__':
	print('connection succeeded')
	app.run(host='0.0.0.0',port=80,debug=True)
