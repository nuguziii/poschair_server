import datetime

from flask import Flask
from flask import g
from flask import redirect
from flask import request
from flask import session
from flask import url_for, abort, render_template, flash
from functools import wraps
from hashlib import md5
from peewee import *

# config - aside from our database, the rest is for use by Flask
DATABASE = 'POSCHAIR.db'
DEBUG = True
SECRET_KEY = 'hin6bab8ge25*r=x&amp;+5$0kn=-#log$pt^#@vrqjld!^2ci@g*b'

# create a flask application - this ``app`` object will be used to handle
# inbound requests, routing them to the proper 'view' functions, etc
app = Flask(__name__)
app.config.from_object(__name__)

# create a peewee database instance -- our models will use this database to
# persist information
database = SqliteDatabase(DATABASE)

# model definitions -- the standard "pattern" is to define a base model class
# that specifies which database to use.  then, any subclasses will automatically
# use the correct storage. for more information, see:
# http://charlesleifer.com/docs/peewee/peewee/models.html#model-api-smells-like-django
class BaseModel(Model):
    class Meta:
        database = database
        db_table = 'users'

# the user model specifies its fields (or columns) declaratively, like django
class User(BaseModel):
    name = CharField()
    password = CharField()
    serialnum = CharField()
    email = CharField(unique=True)


# get the user from the session
#def get_current_user(user):
#    if session.get('logged_in'):
#        return User.get(User.email == user.email)

# view decorator which indicates that the requesting user must be authenticated
# before they can access the view.  it checks the session to see if they're
# logged in, and if not redirects them to the login view.
#def login_required(f):
#    @wraps(f)
#    def inner(*args, **kwargs):
#        if not session.get('logged_in'):
#            return redirect(url_for('login'))
#        return f(*args, **kwargs)
#    return inner

# given a template and a SelectQuery instance, render a paginated list of
# objects from the query inside the template
#def object_list(template_name, qr, var_name='object_list', **kwargs):
#    kwargs.update(
#        page=int(request.args.get('page', 1)),
#        pages=qr.count() / 20 + 1)
#    kwargs[var_name] = qr.paginate(kwargs['page'])
#    return render_template(template_name, **kwargs)

# retrieve a single object matching the specified query or 404 -- this uses the
# shortcut "get" method on model, which retrieves a single object or raises a
# DoesNotExist exception if no matching object exists
# http://charlesleifer.com/docs/peewee/peewee/models.html#Model.get)
def get_object_or_404(model, *expressions):
    try:
        return model.get(*expressions)
    except model.DoesNotExist:
        abort(404)







# Request handlers -- these two hooks are provided by flask and we will use them
# to create and tear down a database connection on each request.
@app.before_request
def before_request():
    print('before_request')
    g.db = database
    g.db.connect()


@app.after_request
def after_request(response):
	print('close_request')
	g.db.close()
	return response

# views -- these are the actual mappings of url to view function
@app.route('/login/', methods=['GET', 'POST'])
def homepage():
	print('login')
	if request.method == 'POST':
		userDetails = request.form
		email = userDetails['email']
		password = userDetails['password']
		try:
			user = User.get(
                    (User.email == request.form['email']) &
                    (User.password == request.form['password']))
		except User.DoesNotExist:
			return 'wrong_pw'

	else:
		return 'success'



@app.route('/signup/', methods=['GET', 'POST'])
def signup():
	print('signup')
	if request.method == 'POST':
		try:
			with database.atomic():
				user = User.create(
					name=request.form['name'],
					password=request.form['password'],#md5((request.form['password']).encode('utf-8')).hexdigest(),
                    serialnum=request.form['serialnumber'],
                    email=request.form['email'])

			return "success"

		except IntegrityError:
			return 'already_existed'

	return render_template('./index.html')


if __name__=='__main__':
	print('connection succeeded')
	app.run(host='0.0.0.0',port=80,debug=True)

