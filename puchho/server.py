from flask import render_template,jsonify,make_response
from flask import abort,send_file
from flask import Flask, session, redirect, url_for, escape, request,Response
from datetime import date
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime, date
from werkzeug import secure_filename
import sys
import pprint
import operator
import json
import time
import os

UPLOAD_FOLDER = '/home/jainsameer/puchho/uploads'
MONGO_URL="ds043971.mlab.com"
MONGO_PORT=43971
MONGO_USER="jainsameer"
MONGO_PWD="jainsameer20"

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'),404

@app.errorhandler(404)
def not_found(error):
    resp = make_response(render_template('page_not_found.html'), 404)
    resp.headers['X-Something'] = 'A value'
    return resp

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['the_file']
        f.save('/var/www/uploads/' + secure_filename(f.filename))

@app.route('/about_us')
def about_us():
	return render_template('about_us.html')

@app.route('/contact_us')
def contact_us():
	return render_template('contact_us.html')

@app.route('/user/<username>')
def show_user_profile(username):

	return render_template('child.html',username=username,user_id=session['user_id'])

@app.route('/post/<int:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return 'Post %d' % (post_id)

@app.route('/projects/')
def projects():
    return 'The project page'

@app.route('/about')
def about():
    return 'The about page'

@app.route('/comment/<comment_id>')
def comment(comment_id):
	comment={}
	try:
		connection = MongoClient(MONGO_URL, MONGO_PORT)
		print "Connected successfully"
		# Get a Database handle to a database named "mydb"
		dbh = connection["skill_trading"]
		dbh.authenticate(MONGO_USER,MONGO_PWD)
		x=dbh.comments.find({"id":int(comment_id)}).count()
		print x
		comments=dbh.comments.find({"id":int(comment_id)})
		for row in comments:
			comment={}
			pprint.pprint(row)
			comment['id']=row['id']
			comment['queryid']=row['queryid']
			comment['user']=row['user']
			comment['upvotes']=row['upvotes']
			comment['message']=row['message']
	except ConnectionFailure, e:
		sys.stderr.write("Could not connect to MongoDB: %s" % e)
	return render_template('comment.html',comment=comment)

@app.route('/submit_user_post')
def submit_user_post():
	message = request.args.get('pos',type=str)
	b = request.args.get('ski',type=str)
	print 'in server'
	skill_arr = json.loads(b)
	print message
	print skill_arr
	try:
		connection = MongoClient(MONGO_URL, MONGO_PORT)
		print "Connected successfully"
		# Get a Database handle to a database named "mydb"
		dbh = connection["skill_trading"]
		dbh.authenticate(MONGO_USER,MONGO_PWD)

		# Demonstrate the db.connection property to retrieve a reference to the
		# Connection object should it go out of scope. In most cases, keeping a
		# reference to the Database object for the lifetime of your program should
		# be sufficient.
		# # assert dbh.connection == c
		print "Successfully set up a database handle"
		count=int(dbh.query.count())
		print count
		ts=time.time()
		query_doc={
		"id":count+1,
		"message":message,
		"user":session['username'],
		"user_id":int(session['user_id']),
		"comment_ids":[],
		"timestamp":ts
		}
		# print skill_arr
		query_skill_doc={
		"id":count+1,
		"skills":skill_arr
		}
		visible=0
		user_id=session['user_id']
		b1=dbh.user_skills.find_one({'id':int(user_id)})['skills']
		b2=skill_arr
		# b2=dbh.query_skills.find_one({'id':int(row['id'])})['skills']
		b3 = [val for val in b1 if val in b2]
		if len(b3)>0:
			visible=1
		dbh.query.insert_one(query_doc)
		dbh.query_skills.insert_one(query_skill_doc)

		# print session['username']
		# return redirect(url_for('user_query',user_id=session['user_id']))
		# return redirect(url_for('show_user_profile',username=username))
	except ConnectionFailure, e:
		sys.stderr.write("Could not connect to MongoDB: %s" % e)
	return jsonify(query_id=count+1,visible=visible)

@app.route('/uploadajax', methods=['POST'])
def upload():
	print request.form['title']
	# file=request.form['file']
	# print request.json['title']
	# print request.json['fn']
	# print request.json['skills']
	# file=request.json['fl']
	file = request.files['file']
	# # c = request.args.get('ski',type=str)
	# # print c
	# # if file and allowed_file(file.filename):
	filename = secure_filename(file.filename)
	print filename
	skill_arr = json.loads(request.form['hidden_skills'])
	print skill_arr
	file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
	return Response('OK')


@app.route('/submit_user_doc', methods=['POST'])
def submit_user_doc():
	file = request.files['file']
	# # c = request.args.get('ski',type=str)
	# # print c
	# # if file and allowed_file(file.filename):
	file_name = secure_filename(file.filename)
	# file_name = request.args.get('pos',type=str)
	title = request.form['title']

	skill_arr = json.loads(request.form['hidden_skills'])
	print title
	print file_name
	print skill_arr

	try:
		connection = MongoClient(MONGO_URL, MONGO_PORT)
		print "Connected successfully"
		# Get a Database handle to a database named "mydb"
		dbh = connection["skill_trading"]
		dbh.authenticate(MONGO_USER,MONGO_PWD)

		# Demonstrate the db.connection property to retrieve a reference to the
		# Connection object should it go out of scope. In most cases, keeping a
		# reference to the Database object for the lifetime of your program should
		# be sufficient.
		# assert dbh.connection == c
		print "Successfully set up a database handle"
		count=int(dbh.doc.count())
		print count
		ts=time.time()
		doc_doc={
		"id":count+1,
		"title":title,
		"file_name":file_name,
		"user":session['username'],
		"user_id":int(session['user_id']),
		"timestamp":ts
		}
		# print skill_arr
		doc_skill_doc={
		"id":count+1,
		"skills":skill_arr
		}
		# visible=0
		# user_id=session['user_id']
		# b1=dbh.user_skills.find_one({'id':int(user_id)})['skills']
		# b2=skill_arr
		# # b2=dbh.query_skills.find_one({'id':int(row['id'])})['skills']
		# b3 = [val for val in b1 if val in b2]
		# if len(b3)>0:
		# 	visible=1
		dbh.doc.insert_one(doc_doc)
		dbh.doc_skills.insert_one(doc_skill_doc)

		# print session['username']
		# return redirect(url_for('user_query',user_id=session['user_id']))
		# return redirect(url_for('show_user_profile',username=username))
	except ConnectionFailure, e:
		sys.stderr.write("Could not connect to MongoDB: %s" % e)
	file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
	return Response('OK')



@app.route('/skills/<skill_id>')
def java_page(skill_id):
	try:
		if session['username']:
			print 'first',session['username']
			user_id=session['user_id']
			try:
				connection = MongoClient(MONGO_URL, MONGO_PORT)
				print "Connected successfully"
				# Get a Database handle to a database named "mydb"
				dbh = connection["skill_trading"]
				dbh.authenticate(MONGO_USER,MONGO_PWD)
				skill_list=dbh.user_skills.find_one({'id':int(user_id)})['skills']
				print skill_list
				if int(skill_id) in skill_list:
					skill_query_list=[]
					query_id_list=[]
					query_skills_table=dbh.query_skills.find({})
					for row in query_skills_table:
						if int(skill_id) in row['skills']:
							query_id_list.append(row['id'])
					print query_id_list
					for query_id in query_id_list:
						skill_query_list.append(dbh.query.find_one({'id':int(query_id)}))
					skill_query_list=sorted(skill_query_list,key=operator.itemgetter('timestamp'),reverse=True)
					title=dbh.skills.find_one({'id':int(skill_id)})['name']
					print title
					return render_template('java.html',title=title,username=session['username'],skill_query_list=skill_query_list)
				else:
					return redirect(url_for('page_not_found',error='kabil to ban pehle'))
			except ConnectionFailure, e:
				sys.stderr.write("Could not connect to MongoDB: %s" % e)
			return redirect(url_for('log_the_user_in',username=session['username']))
		else:
			print 'second'
			return redirect(url_for('page_not_found',error='pehle login to kar'))
	except:
		print 'third'
		# print session['username']
		session['username']=None
		return redirect(url_for('page_not_found',error='pehle login to kar'))

@app.route('/user_dashboard_form/<user_id>')
def user_dashboard_form(user_id):
	if not valid_user(user_id):
		return redirect(url_for('index'))
	skill_list=[]
	try:
		connection = MongoClient(MONGO_URL, MONGO_PORT)
		print "Connected successfully"
		# Get a Database handle to a database named "mydb"
		dbh = connection["skill_trading"]
		dbh.authenticate(MONGO_USER,MONGO_PWD)
		skill_table=dbh.skills.find({})
		user_skill=dbh.user_skills.find_one({"id":int(user_id)})['skills']
		for row in skill_table:
			if row['id'] in user_skill:
				continue
			else:
				skill_doc={}
				skill_doc['id']=int(row['id'])
				skill_doc['name']=row['name']
				skill_list.append(skill_doc)
	except ConnectionFailure, e:
		sys.stderr.write("Could not connect to MongoDB: %s" % e)
	return render_template('user_dashboard.html',skill_list=skill_list)

@app.route('/user_dashboard', methods=['POST', 'GET'])
def user_dashboard():
	print request.method
	account_picks = request.form.getlist('skill_picks')
	print account_picks
	return redirect(url_for('index'))



@app.route('/user_query/<user_id>')
def user_query(user_id):
	if not valid_user(user_id):
		return redirect(url_for('index'))
	user_query={}
	skill_list=[]
	try:
		connection = MongoClient(MONGO_URL, MONGO_PORT)
		print "Connected successfully"
		# Get a Database handle to a database named "mydb"
		dbh = connection["skill_trading"]
		dbh.authenticate(MONGO_USER,MONGO_PWD)
		x=dbh.users.find_one({"id":int(user_id)})
		# print x
		user_query['user']=x['username']
		user_query['queries']=[]
		user_query_table=dbh.query.find({"user_id":int(user_id)})
		for row in user_query_table:
			user_query_set={}
			user_query_set['queries']=row
			user_query_set['visible']=0
			b1=dbh.user_skills.find_one({'id':int(user_id)})['skills']
			b2=dbh.query_skills.find_one({'id':int(row['id'])})['skills']
			b3 = [val for val in b1 if val in b2]
			# print "b1"
			# print b1
			# print "b2"
			# print b2
			# print "b3"
			# print b3
			if len(b3)>0:
				user_query_set['visible']=1
			user_query['queries'].append(user_query_set)
		skill_table=dbh.skills.find({})
		for row in skill_table:
			skill={}
			skill['id']=int(row['id'])
			skill['name']=row['name']
			skill_list.append(skill)
	except ConnectionFailure, e:
		sys.stderr.write("Could not connect to MongoDB: %s" % e)
	return render_template("user_queries.html",user_query=user_query,skill_list=skill_list)


@app.route('/query/<query_id>/<visible>')
def query(query_id,visible):
	query={}
	query_skill_list=[]
	user_skill_ids=[]
	try:
		connection = MongoClient(MONGO_URL, MONGO_PORT)
		print "Connected successfully"
		# Get a Database handle to a database named "mydb"
		dbh = connection["skill_trading"]
		dbh.authenticate(MONGO_USER,MONGO_PWD)
		x=dbh.query.find({"id":int(query_id)}).count()
		# print x
		queries=dbh.query.find({"id":int(query_id)})
		user_skill_ids=dbh.user_skills.find_one({'id':session['user_id']})['skills']
		for row in queries:
			query={}
			# pprint.pprint(row)
			query['id']=row['id']
			query['user']=row['user']
			query['user_id']=row['user_id']
			query['message']=row['message']
			seconds=int((time.time()-row['timestamp']))
			# print seconds
			# print strftime("%a, %d %b %Y %H:%M:%S +0000", time.time())
			# print time.asctime( time.localtime(time.time()) )
			# print time.asctime( time.localtime(row['timestamp']))
			# print time.time()
			# print row['timestamp']
			mess="seconds"
			if seconds>=60:
				seconds=seconds/60
				mess="minutes"
				if seconds>=60:
					seconds=seconds/60
					mess="hours"
					if seconds>=24:
						seconds=seconds/24
						mess="days"
						if seconds>=30:
							seconds=seconds/30
							mess="months"
							if seconds>=12:
								seconds=seconds/12
								mess="years"
			if seconds==1:
				mess=mess[:-1]

			mess="asked "+str(seconds)+" "+mess+" ago"
			query['timestamp']=mess
			# pprint.pprint(query)
			comment_ids=[]
			comment_ids=row['comment_ids']
			map1={}
			temp_comments=[]
			for comment_id in comment_ids:
				temp_comment=dbh.comments.find_one({"id":int(comment_id)})
				# pprint.pprint(temp_comment)
				map1[comment_id]=temp_comment['upvotes']
			sorted_x = sorted(map1.items(), key=operator.itemgetter(1),reverse=True)
			for i in range(len(sorted_x)):
				# print sorted_x[i][0]
				temp_comment=dbh.comments.find_one({"id":int(sorted_x[i][0])})
				temp_comment['liked']=False
				like_ids=[]
				x=dbh.comment_likes.find({'id':int(temp_comment['id'])}).count()
				if x>0:
					like_ids=dbh.comment_likes.find_one({'id':int(temp_comment['id'])})['likes']
				if int(session['user_id']) in like_ids:
					temp_comment['liked']=True
				seconds=int((time.time()-temp_comment['timestamp']))
				mess="seconds"
				if seconds>=60:
					seconds=seconds/60
					mess="minutes"
					if seconds>=60:
						seconds=seconds/60
						mess="hours"
						if seconds>=24:
							seconds=seconds/24
							mess="days"
							if seconds>=30:
								seconds=seconds/30
								mess="months"
								if seconds>=12:
									seconds=seconds/12
									mess="years"
				if seconds==1:
					mess=mess[:-1]

				mess="answered "+str(seconds)+" "+mess+" ago"
				temp_comment['timestamp']=mess
				temp_comments.append(temp_comment)

			query['comments']=temp_comments


			skill_ids=dbh.query_skills.find_one({'id':int(query_id)})['skills']
			# print skill_ids
			for skill_id in skill_ids:
				skill_set=dbh.skills.find_one({'id':int(skill_id)})
				query_skill_list.append(skill_set)
			# print query_skill_list
	except ConnectionFailure, e:
		sys.stderr.write("Could not connect to MongoDB: %s" % e)
	return render_template('query.html',query=query,user_skill_ids=user_skill_ids,visible=int(visible),query_skill_list=query_skill_list)


@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
	try:
		print filename
		# buf = io.BytesIO()
		# buf.write('hello world')
		# buf.seek(0)
		# return send_file(buf,attachment_filename="testing.txt",as_attachment=True)
		file_name=UPLOAD_FOLDER+'/'+filename
		return send_file(file_name, attachment_filename=filename)
	except Exception as e:
		return str(e)
    # uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    # uploads=UPLOAD_FOLDER
    # return send_from_directory(directory=uploads, filename=filename)


@app.route('/doc/<doc_id>')
def doc(doc_id):
	doc={}
	doc_skill_list=[]
	user_skill_ids=[]
	try:
		connection = MongoClient(MONGO_URL, MONGO_PORT)
		print "Connected successfully"
		# Get a Database handle to a database named "mydb"
		dbh = connection["skill_trading"]
		dbh.authenticate(MONGO_USER,MONGO_PWD)
		# x=dbh.doc.find({"id":int(doc_id)}).count()
		# print x
		doc=dbh.doc.find_one({"id":int(doc_id)})
		user_skill_ids=dbh.user_skills.find_one({'id':session['user_id']})['skills']
		skill_ids=dbh.doc_skills.find_one({'id':int(doc_id)})['skills']
		# print skill_ids
		for skill_id in skill_ids:
			skill_set=dbh.skills.find_one({'id':int(skill_id)})
			doc_skill_list.append(skill_set)
		# print doc_skill_list
	except ConnectionFailure, e:
		sys.stderr.write("Could not connect to MongoDB: %s" % e)
	return render_template('document.html',doc=doc,user_skill_ids=user_skill_ids,doc_skill_list=doc_skill_list)

def valid_login(email,password):
	try:
		connection = MongoClient(MONGO_URL, MONGO_PORT)
		print "Connected successfully"
		# Get a Database handle to a database named "mydb"
		dbh = connection["skill_trading"]
		dbh.authenticate(MONGO_USER,MONGO_PWD)
		count=dbh.users.find({'email':email,'password':password}).count()
		if count==1:
			return True
	except ConnectionFailure, e:
		sys.stderr.write("Could not connect to MongoDB: %s" % e)
	return False

def valid_user(user_id):
	try:
		if session['username']:
			if int(session['user_id'])==int(user_id):
				return True
			# print 'first',session['username']
			# return True
			# return redirect(url_for('log_the_user_in',username=session['username']))
		else:
			print 'second'
			return False
	except:
		print 'third'
		session['username']=None
		session['user_id']=None
		return False


@app.route('/')
def index():
	try:
		if session['username']:
			print 'first',session['username']
			# return render_template('puchho.html',user_id=session['user_id'])
			return redirect(url_for('puchho',user_id=session['user_id']))
		else:
			print 'second'
			return render_template('home.html')
	except:
		print 'third'
		session['username']=None
		session['user_id']=None
		return redirect(url_for('index'))




def log_the_user_in(username):

	session['username']=username
	return redirect(url_for('show_user_profile',username=username))


@app.route('/register_form')
def register_form():
	return render_template('register.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
	error = None
	print "sameer"
	if request.method == 'POST':
		first_name=request.form['first_name']
		last_name=request.form['last_name']
		phone=request.form['phone']
		password=request.form['password']
		username=first_name
		email=request.form['email']
		print first_name,last_name,phone,password,username,email
		try:
			connection = MongoClient(MONGO_URL, MONGO_PORT)
			print "Connected successfully"
			# Get a Database handle to a database named "mydb"
			dbh = connection["skill_trading"]
			dbh.authenticate(MONGO_USER,MONGO_PWD)
			print "database connected"
			# Demonstrate the db.connection property to retrieve a reference to the
			# Connection object should it go out of scope. In most cases, keeping a
			# reference to the Database object for the lifetime of your program should
			# be sufficient.
			# assert dbh.connection == c
			print "Successfully set up a database handle"
			count=int(dbh.users.count())
			print "table connected"
			user_doc={
			"id":count+1,
			"username":first_name,
			"first_name" : first_name,
			"last_name" : last_name,
			"phone" : phone,
			"email" : email,
			"password" : password,
			"register_date":str(date.today())
			}
			user_skill_doc={
			"id":count+1,
			"skills":[]
			}
			x=dbh.users.find({'username':first_name,'password':password}).count()
			if x>=1:
				return redirect(url_for('login_form'))
			dbh.users.insert_one(user_doc)
			dbh.user_skills.insert_one(user_skill_doc)
			session['username']=username
			session['user_id']=count+1
			print session['username']
			return redirect(url_for('dashboard',user_id=session['user_id']))
			# return redirect(url_for('show_user_profile',username=username))
		except ConnectionFailure, e:
			sys.stderr.write("Could not connect to MongoDB: %s" % e)
	# return redirect(url_for('index'))
	return render_template('register.html')

@app.route('/login_form')
def login_form():
	return render_template('login.html',font_url='//fonts.googleapis.com/css?family=Open+Sans:400,300,600,700,800')

@app.route('/login',methods = ['POST', 'GET'])
def login():
	if request.method == 'POST':
		email=request.form['email']
		# user = request.form['username']
		password=request.form['password']
		if valid_login(email,password):
			# session['username']=user
			try:
				connection = MongoClient(MONGO_URL, MONGO_PORT)
				print "Connected successfully"
				# Get a Database handle to a database named "mydb"
				dbh = connection["skill_trading"]
				dbh.authenticate(MONGO_USER,MONGO_PWD)
				session['user_id']=int(dbh.users.find_one({'email':email,'password':password})['id'])
				session['username']=dbh.users.find_one({'email':email,'password':password})['username']
				user=session['username']
				print session['username']
				return redirect(url_for('puchho',user_id=session['user_id']))
				# return render_template('child.html')
				# return redirect(url_for('show_user_profile',username=user))
			except ConnectionFailure, e:
				sys.stderr.write("Could not connect to MongoDB: %s" % e)

			return redirect(url_for('login_form'))
		else:
			return redirect(url_for('login_form'))
		# return redirect(url_for('success',name = user))
	else:
		user = request.args.get('username')
		return redirect(url_for('show_user_profile',username=user))
	return redirect(url_for('register'))


@app.route('/logout')
def logout():
	session['username']=None
	session['user_id']=None
	session.pop(session['username'], None)
	session.pop(session['user_id'], None)
	return redirect(url_for('index'))

@app.route('/dashboard/<user_id>')
def dashboard(user_id):
	if int(user_id)!=int(session['user_id']):
		return redirect(url_for('profile',user_id=user_id))
	# if not valid_user(user_id):
	# 	return redirect(url_for('index'))
	ay_present=0
	ay_text=""
	work_list=[]
	edu_list=[]
	rem_social=[]
	social=[]
	skill_list=[]
	not_skill_list=[]
	resume_present=0
	resume_dict={}
	try:
		connection = MongoClient(MONGO_URL, MONGO_PORT)
		print "Connected successfully"
		dbh = connection["skill_trading"]
		dbh.authenticate(MONGO_USER,MONGO_PWD)
		x=dbh.ay.find({'user_id':int(user_id)}).count()
		if x>0:
			ay_present=1
			ay_text=dbh.ay.find_one({'user_id':int(user_id)})['text']
		work_table=dbh.work_exp.find({'user_id':int(user_id)})
		edu_table=dbh.edu_exp.find({'user_id':int(user_id)})
		for row in work_table:
			work_list.append(row)
		for row in edu_table:
			edu_list.append(row)

		rem_social.append('Facebook')
		rem_social.append('LinkedIn')
		rem_social.append('Twitter')
		x=dbh.user_social_profiles.find({'id':int(user_id)}).count()
		if x>0:
			social_profiles=dbh.user_social_profiles.find_one({'id':int(user_id)})['profiles']
			for profile in social_profiles:
				social.append(profile)
				rem_social.remove(profile['name'])

		skill_ids=[]
		x=dbh.user_skills.find({'id':int(user_id)}).count()
		if x>0:
			skill_ids=dbh.user_skills.find_one({'id':int(user_id)})['skills']
		skill_table=dbh.skills.find({})
		for row in skill_table:
			if int(row['id']) in skill_ids:
				skill_set=row
				skill_list.append(skill_set)
			else:
				not_skill_list.append(row['name'])

		x=dbh.resume.find({'user_id':int(user_id)}).count()
		if x>0:
			resume_present=1
			resume_dict=dbh.resume.find_one({'user_id':int(user_id)})
	except ConnectionFailure, e:
		sys.stderr.write("Could not connect to MongoDB: %s" % e)

	return render_template('dashboard.html',ay_present=ay_present,ay_text=ay_text,work_list=work_list,edu_list=edu_list,rem_social=json.dumps(rem_social),social=social,skill_list=skill_list,rem=json.dumps(not_skill_list),resume_present=resume_present,resume_dict=resume_dict)

@app.route('/profile/<user_id>')
def profile(user_id):
	if int(user_id)==int(session['user_id']):
		return redirect(url_for('dashboard',user_id=user_id))
	user_name=""
	ay_present=0
	ay_text=""
	work_list=[]
	edu_list=[]
	rem_social=[]
	social=[]
	skill_list=[]
	not_skill_list=[]
	resume_present=0
	resume_dict={}
	try:
		connection = MongoClient(MONGO_URL, MONGO_PORT)
		print "Connected successfully"
		# Get a Database handle to a database named "mydb"
		dbh = connection["skill_trading"]
		dbh.authenticate(MONGO_USER,MONGO_PWD)
		user_name=dbh.users.find_one({'id':int(user_id)})['username']
		x=dbh.ay.find({'user_id':int(user_id)}).count()
		if x>0:
			ay_present=1
			ay_text=dbh.ay.find_one({'user_id':int(user_id)})['text']
		work_table=dbh.work_exp.find({'user_id':int(user_id)})
		edu_table=dbh.edu_exp.find({'user_id':int(user_id)})
		for row in work_table:
			work_list.append(row)
		for row in edu_table:
			edu_list.append(row)

		rem_social.append('Facebook')
		rem_social.append('LinkedIn')
		rem_social.append('Twitter')
		x=dbh.user_social_profiles.find({'id':int(user_id)}).count()
		if x>0:
			social_profiles=dbh.user_social_profiles.find_one({'id':int(user_id)})['profiles']
			for profile in social_profiles:
				social.append(profile)
				rem_social.remove(profile['name'])

		x=dbh.user_skills.find({'id':int(user_id)}).count()
		skill_ids=[]
		if x>0:
			skill_ids=dbh.user_skills.find_one({'id':int(user_id)})['skills']
		skill_table=dbh.skills.find({})
		for row in skill_table:
			if int(row['id']) in skill_ids:
				skill_set=row
				skill_list.append(skill_set)
			else:
				not_skill_list.append(row['name'])

		x=dbh.resume.find({'user_id':int(user_id)}).count()
		if x>0:
			resume_present=1
			resume_dict=dbh.resume.find_one({'user_id':int(user_id)})
	except ConnectionFailure, e:
		sys.stderr.write("Could not connect to MongoDB: %s" % e)

	return render_template('profile.html',user_name=user_name,ay_present=ay_present,ay_text=ay_text,work_list=work_list,edu_list=edu_list,rem_social=json.dumps(rem_social),social=social,skill_list=skill_list,rem=json.dumps(not_skill_list),resume_present=resume_present,resume_dict=resume_dict)


@app.route('/puchho/<user_id>')
def puchho(user_id):
	if not valid_user(user_id):
		return redirect(url_for('index'))
	user_query_list=[]
	skill_list=[]
	user_skill_list=[]
	answered_query=[]
	try:
		connection = MongoClient(MONGO_URL, MONGO_PORT)
		print "Connected successfully"
		# Get a Database handle to a database named "mydb"
		dbh = connection["skill_trading"]
		dbh.authenticate(MONGO_USER,MONGO_PWD)
		x=dbh.users.find_one({"id":int(user_id)})
		# print x
		# user_query['user']=x['username']
		# user_query['queries']=[]
		user_query_table=dbh.query.find({"user_id":int(user_id)})
		map2={}
		for row in user_query_table:
			map2[row['id']]=row['timestamp']
		sorted_y = sorted(map2.items(), key=operator.itemgetter(1),reverse=True)
		for i in range(len(sorted_y)):
			temp_query=dbh.query.find_one({'id':int(sorted_y[i][0])})
			user_query_set={}
			user_query_set['query']=temp_query
			user_query_set['visible']=0
			b1=dbh.user_skills.find_one({'id':int(user_id)})['skills']
			b2=dbh.query_skills.find_one({'id':int(temp_query['id'])})['skills']
			b3 = [val for val in b1 if val in b2]
			if len(b3)>0:
				user_query_set['visible']=1
			user_query_list.append(user_query_set)

		# for row in user_query_table:
		# 	user_query_set={}
		# 	user_query_set['queries']=row
		# 	user_query_set['visible']=0
		# 	b1=dbh.user_skills.find_one({'id':int(user_id)})['skills']
		# 	b2=dbh.query_skills.find_one({'id':int(row['id'])})['skills']
		# 	b3 = [val for val in b1 if val in b2]
		# 	# print "b1"
		# 	# print b1
		# 	# print "b2"
		# 	# print b2
		# 	# print "b3"
		# 	# print b3
		# 	if len(b3)>0:
		# 		user_query_set['visible']=1
		# 	user_query['queries'].append(user_query_set)
		skill_table=dbh.skills.find({})
		for row in skill_table:
			skill={}
			skill['id']=int(row['id'])
			skill['name']=row['name']
			skill_list.append(skill)
		comment_table=dbh.comments.find({'user_id':int(user_id)})
		map1={}
		for row in comment_table:
			map1[row['id']]=row['timestamp']
		sorted_x = sorted(map1.items(), key=operator.itemgetter(1),reverse=True)
		already_in_queue=[]
		for i in range(len(sorted_x)):
			temp_comment=dbh.comments.find_one({'id':int(sorted_x[i][0])})
			temp_query=dbh.query.find_one({'id':int(temp_comment['queryid'])})
			if temp_query['id'] not in already_in_queue:
				answered_query.append(temp_query)
				already_in_queue.append(temp_query['id'])

		user_skill_ids=[]
		x=dbh.user_skills.find({'id':int(user_id)}).count()
		if x>0:
			user_skill_ids=dbh.user_skills.find_one({'id':int(user_id)})['skills']
		for skill_id in user_skill_ids:
			temp_skill=dbh.skills.find_one({'id':int(skill_id)})
			user_skill_list.append(temp_skill)
	except ConnectionFailure, e:
		sys.stderr.write("Could not connect to MongoDB: %s" % e)
	return render_template("puchho.html",user_query_list=user_query_list,skill_list=skill_list,answered_query=answered_query,user_skill_list=user_skill_list)

@app.route('/submit_user_comment')
def submit_user_comment():
	message=request.args.get('message',type=str)
	queryid=request.args.get('queryid',type=int)
	print message,queryid
	ts=time.time()
	try:
		connection = MongoClient(MONGO_URL, MONGO_PORT)
		print "Connected successfully"
		# Get a Database handle to a database named "mydb"
		dbh = connection["skill_trading"]
		dbh.authenticate(MONGO_USER,MONGO_PWD)
		x=dbh.comments.find({}).count()
		comment_doc={
		'id':x+1,
		'message':message,
		'queryid':queryid,
		'timestamp':ts,
		'upvotes':0,
		'user':session['username'],
		'user_id':session['user_id']
		}
		comment_likes_doc={
		'id':x+1,
		'likes':[]
		}
		query_doc=dbh.query.find_one({'id':queryid})
		query_doc['comment_ids'].append(x+1)
		dbh.query.remove({'id':queryid})
		dbh.query.insert_one(query_doc)
		dbh.comment_likes.insert_one(comment_likes_doc)
		dbh.comments.insert_one(comment_doc)
	except ConnectionFailure, e:
		sys.stderr.write("Could not connect to MongoDB: %s" % e)

	return jsonify(done=1,id=x+1)

@app.route('/submit_user_like')
def submit_user_like():
	comment_id=request.args.get('comment_id',type=int)
	print comment_id
	try:
		connection = MongoClient(MONGO_URL, MONGO_PORT)
		print "Connected successfully"
		# Get a Database handle to a database named "mydb"
		dbh = connection["skill_trading"]
		dbh.authenticate(MONGO_USER,MONGO_PWD)
		temp_comment=dbh.comments.find_one({'id':comment_id})
		temp_comment_likes=dbh.comment_likes.find_one({'id':comment_id})
		dbh.comments.remove({'id':comment_id})
		dbh.comment_likes.remove({'id':comment_id})
		temp_comment['upvotes']=temp_comment['upvotes']+1
		temp_comment_likes['likes'].append(session['user_id'])
		dbh.comments.insert_one(temp_comment)
		dbh.comment_likes.insert_one(temp_comment_likes)
	except ConnectionFailure, e:
		sys.stderr.write("Could not connect to MongoDB: %s" % e)
	return jsonify(done=1)

@app.route('/submit_user_ay')
def submit_user_ay():
	ay_text=request.args.get('ay_text',type=str)
	try:
		connection = MongoClient(MONGO_URL, MONGO_PORT)
		print "Connected successfully"
		# Get a Database handle to a database named "mydb"
		dbh = connection["skill_trading"]
		dbh.authenticate(MONGO_USER,MONGO_PWD)
		ay_doc={
		'user_id':int(session['user_id']),
		'text':ay_text
		}
		dbh.ay.insert_one(ay_doc)
	except ConnectionFailure, e:
		sys.stderr.write("Could not connect to MongoDB: %s" % e)
	return jsonify(done=1)

@app.route('/submit_user_work')
def submit_user_work():


	cw=request.args.get('cur_work',type=int)
	st_date=request.args.get('st_date',type=str)
	# print st_date
	end_date=request.args.get('end_date',type=str)
	org=request.args.get('org',type=str)
	des=request.args.get('des',type=str)
	dis=request.args.get('dis',type=str)
	if cw==1:
		cur_work=True
	else:
		cur_work=False
	print st_date,end_date,org,des,dis
	try:
		connection = MongoClient(MONGO_URL, MONGO_PORT)
		print "Connected successfully"
		# Get a Database handle to a database named "mydb"
		dbh = connection["skill_trading"]
		dbh.authenticate(MONGO_USER,MONGO_PWD)
		work_exp_doc={
		'user_id':session['user_id'],
		'cur_work':cur_work,
		'st_date':str(st_date),
		'end_date':str(end_date),
		'org':str(org),
		'des':str(des),
		'dis':str(dis)
		}
		dbh.work_exp.insert_one(work_exp_doc)
	except ConnectionFailure, e:
		sys.stderr.write("Could not connect to MongoDB: %s" % e)
	return jsonify(result=1)

@app.route('/account_settings/<user_id>')
def account_settings(user_id):
	user_doc={}
	try:
		connection = MongoClient(MONGO_URL, MONGO_PORT)
		print "Connected successfully"
		# Get a Database handle to a database named "mydb"
		dbh = connection["skill_trading"]
		dbh.authenticate(MONGO_USER,MONGO_PWD)
		user_doc=dbh.users.find_one({'id':int(user_id)})
	except ConnectionFailure, e:
		sys.stderr.write("Could not connect to MongoDB: %s" % e)
	return render_template('account_settings.html',user_doc=user_doc)

@app.route('/change_first_name')
def change_first_name():
	user_id=request.args.get('user_id',type=int)
	first_name=request.args.get('first_name',type=str)
	try:
		connection = MongoClient(MONGO_URL, MONGO_PORT)
		print "Connected successfully"
		# Get a Database handle to a database named "mydb"
		dbh = connection["skill_trading"]
		dbh.authenticate(MONGO_USER,MONGO_PWD)
		temp_user_doc=dbh.users.find_one({'id':int(user_id)})
		temp_user_doc['first_name']=first_name
		temp_user_doc['username']=first_name
		session['username']=first_name
		dbh.users.remove({'id':int(user_id)})
		dbh.users.insert_one(temp_user_doc)
	except ConnectionFailure, e:
		sys.stderr.write("Could not connect to MongoDB: %s" % e)
		return jsonify(done=0)
	return jsonify(done=1)

@app.route('/change_last_name')
def change_last_name():
	user_id=request.args.get('user_id',type=int)
	last_name=request.args.get('last_name',type=str)
	try:
		connection = MongoClient(MONGO_URL, MONGO_PORT)
		print "Connected successfully"
		# Get a Database handle to a database named "mydb"
		dbh = connection["skill_trading"]
		dbh.authenticate(MONGO_USER,MONGO_PWD)
		temp_user_doc=dbh.users.find_one({'id':int(user_id)})
		temp_user_doc['last_name']=last_name
		dbh.users.remove({'id':int(user_id)})
		dbh.users.insert_one(temp_user_doc)
	except ConnectionFailure, e:
		sys.stderr.write("Could not connect to MongoDB: %s" % e)
		return jsonify(done=0)
	return jsonify(done=1)

@app.route('/change_phone')
def change_phone():
	user_id=request.args.get('user_id',type=int)
	phone=request.args.get('phone',type=str)
	try:
		connection = MongoClient(MONGO_URL, MONGO_PORT)
		print "Connected successfully"
		# Get a Database handle to a database named "mydb"
		dbh = connection["skill_trading"]
		dbh.authenticate(MONGO_USER,MONGO_PWD)
		temp_user_doc=dbh.users.find_one({'id':int(user_id)})
		temp_user_doc['phone']=phone
		dbh.users.remove({'id':int(user_id)})
		dbh.users.insert_one(temp_user_doc)
	except ConnectionFailure, e:
		sys.stderr.write("Could not connect to MongoDB: %s" % e)
		return jsonify(done=0)
	return jsonify(done=1)

@app.route('/change_password')
def change_password():
	user_id=request.args.get('user_id',type=int)
	password=request.args.get('password',type=str)
	try:
		connection = MongoClient(MONGO_URL, MONGO_PORT)
		print "Connected successfully"
		# Get a Database handle to a database named "mydb"
		dbh = connection["skill_trading"]
		dbh.authenticate(MONGO_USER,MONGO_PWD)
		temp_user_doc=dbh.users.find_one({'id':int(user_id)})
		temp_user_doc['password']=password
		dbh.users.remove({'id':int(user_id)})
		dbh.users.insert_one(temp_user_doc)
	except ConnectionFailure, e:
		sys.stderr.write("Could not connect to MongoDB: %s" % e)
		return jsonify(done=0)
	return jsonify(done=1)

@app.route('/delete_user_work')
def delete_user_work():

	print "in server"
	cw=request.args.get('cur_work',type=int)
	st_date=request.args.get('st_date',type=str)
	# print st_date
	end_date=request.args.get('end_date',type=str)
	org=request.args.get('org',type=str)
	des=request.args.get('des',type=str)
	dis=request.args.get('dis',type=str)
	if cw==1:
		cur_work=True
	else:
		cur_work=False
	print cur_work,st_date,end_date,org,des,dis
	try:
		connection = MongoClient(MONGO_URL, MONGO_PORT)
		print "Connected successfully"
		# Get a Database handle to a database named "mydb"
		dbh = connection["skill_trading"]
		dbh.authenticate(MONGO_USER,MONGO_PWD)
		work_exp_doc={
		'user_id':session['user_id'],
		'cur_work':cur_work,
		'st_date':str(st_date),
		'end_date':str(end_date),
		'org':str(org),
		'des':str(des),
		'dis':str(dis)
		}
		dbh.work_exp.remove(work_exp_doc)

	except ConnectionFailure, e:
		sys.stderr.write("Could not connect to MongoDB: %s" % e)
		return jsonify(result=1,found=0)
	return jsonify(result=1,found=1)

@app.route('/submit_user_edu')
def submit_user_edu():


	cw=request.args.get('cur_edu',type=int)
	st_date=request.args.get('st_date',type=str)
	# print st_date
	end_date=request.args.get('end_date',type=str)
	ins=request.args.get('ins',type=str)
	deg=request.args.get('deg',type=str)

	if cw==1:
		cur_edu=True
	else:
		cur_edu=False
	print st_date,end_date,ins,deg
	try:
		connection = MongoClient(MONGO_URL, MONGO_PORT)
		print "Connected successfully"
		# Get a Database handle to a database named "mydb"
		dbh = connection["skill_trading"]
		dbh.authenticate(MONGO_USER,MONGO_PWD)
		edu_exp_doc={
		'user_id':session['user_id'],
		'cur_edu':cur_edu,
		'st_date':str(st_date),
		'end_date':str(end_date),
		'ins':str(ins),
		'deg':str(deg)
		}
		dbh.edu_exp.insert_one(edu_exp_doc)
	except ConnectionFailure, e:
		sys.stderr.write("Could not connect to MongoDB: %s" % e)
	return jsonify(result=1)

@app.route('/delete_user_edu')
def delete_user_edu():

	print "in server"
	cw=request.args.get('cur_edu',type=int)
	st_date=request.args.get('st_date',type=str)
	# print st_date
	end_date=request.args.get('end_date',type=str)
	ins=request.args.get('ins',type=str)
	deg=request.args.get('deg',type=str)
	if cw==1:
		cur_edu=True
	else:
		cur_edu=False
	print cur_edu,st_date,end_date,ins,deg
	try:
		connection = MongoClient(MONGO_URL, MONGO_PORT)
		print "Connected successfully"
		# Get a Database handle to a database named "mydb"
		dbh = connection["skill_trading"]
		dbh.authenticate(MONGO_USER,MONGO_PWD)
		edu_exp_doc={
		'user_id':session['user_id'],
		'cur_edu':cur_edu,
		'st_date':str(st_date),
		'end_date':str(end_date),
		'ins':str(ins),
		'deg':str(deg)
		}
		dbh.edu_exp.remove(edu_exp_doc)

	except ConnectionFailure, e:
		sys.stderr.write("Could not connect to MongoDB: %s" % e)
		return jsonify(result=1,found=0)
	return jsonify(result=1,found=1)

@app.route('/submit_user_social_profile')
def submit_user_social_profile():
	profile_name=request.args.get('profile_name',type=str)
	profile_value=request.args.get('profile_value',type=str)
	user_id=int(session['user_id'])
	profiles=[]
	try:
		connection = MongoClient(MONGO_URL, MONGO_PORT)
		print "Connected successfully"
		# Get a Database handle to a database named "mydb"
		dbh = connection["skill_trading"]
		dbh.authenticate(MONGO_USER,MONGO_PWD)
		x=dbh.user_social_profiles.find({'id':user_id}).count()
		if x>0:
			profiles=dbh.user_social_profiles.find_one({'id':user_id})['profiles']
			dbh.user_social_profiles.remove({'id':user_id})

		profile_dict={}
		profile_dict['name']=profile_name
		profile_dict['value']=profile_value
		profiles.append(profile_dict)

		profile_doc={
		'id':user_id,
		'profiles':profiles
		}
		dbh.user_social_profiles.insert_one(profile_doc)
	except ConnectionFailure, e:
		sys.stderr.write("Could not connect to MongoDB: %s" % e)
	return jsonify(done=1)


@app.route('/submit_user_skill')
def submit_user_skill():
	skill_id=request.args.get('skill_id',type=int)
	if skill_id==None:
		print skill_id
		return jsonify(done=0)
	user_id=int(session['user_id'])
	try:
		connection = MongoClient(MONGO_URL, MONGO_PORT)
		print "Connected successfully"
		# Get a Database handle to a database named "mydb"
		dbh = connection["skill_trading"]
		dbh.authenticate(MONGO_USER,MONGO_PWD)
		skill_ids=[]
		x=dbh.user_skills.find({'id':user_id}).count()
		if x>0:
			skill_ids=dbh.user_skills.find_one({'id':user_id})['skills']
		dbh.user_skills.remove({'id':user_id})
		skill_ids.append(skill_id)
		user_skill_doc={
		'id':user_id,
		'skills':skill_ids
		}
		dbh.user_skills.insert_one(user_skill_doc)
		print skill_id
	except ConnectionFailure, e:
		sys.stderr.write("Could not connect to MongoDB: %s" % e)

	return jsonify(done=1)

@app.route('/submit_user_resume', methods=['POST'])
def submit_user_resume():
	print "in resume"
	file = request.files['file']
	file_name = secure_filename(file.filename)
	print file_name
	try:
		connection = MongoClient(MONGO_URL, MONGO_PORT)
		print "Connected successfully"
		# Get a Database handle to a database named "mydb"
		dbh = connection["skill_trading"]
		dbh.authenticate(MONGO_USER,MONGO_PWD)

		# Demonstrate the db.connection property to retrieve a reference to the
		# Connection object should it go out of scope. In most cases, keeping a
		# reference to the Database object for the lifetime of your program should
		# be sufficient.
		# assert dbh.connection == c
		print "Successfully set up a database handle"
		count=int(dbh.resume.count())
		print count
		ts=time.time()
		resume_doc={
		"id":count+1,
		"file_name":file_name,
		"user":session['username'],
		"user_id":int(session['user_id']),
		"timestamp":ts
		}
		# print skill_arr

		# visible=0
		# user_id=session['user_id']
		# b1=dbh.user_skills.find_one({'id':int(user_id)})['skills']
		# b2=skill_arr
		# # b2=dbh.query_skills.find_one({'id':int(row['id'])})['skills']
		# b3 = [val for val in b1 if val in b2]
		# if len(b3)>0:
		# 	visible=1
		dbh.resume.insert_one(resume_doc)
		# dbh.doc_skills.insert_one(doc_skill_doc)

		# print session['username']
		# return redirect(url_for('user_query',user_id=session['user_id']))
		# return redirect(url_for('show_user_profile',username=username))
	except ConnectionFailure, e:
		sys.stderr.write("Could not connect to MongoDB: %s" % e)
	file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
	return jsonify(file_name=file_name)



def allowed_file(filename):
	return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/get_Tags_List',methods=['POST', 'GET'])
def get_Tags_List():
	user_id=int(session['user_id'])
	results=[]
	results.append('C')
	results.append('C++')
	results.append('Python')
	return json.dumps({"suggestions":results})



@app.route('/seekho')
def seekho():
	doc_list=[]
	# name_list=""
	try:
		connection = MongoClient(MONGO_URL, MONGO_PORT)
		print "Connected successfully"
		# Get a Database handle to a database named "mydb"
		dbh = connection["skill_trading"]
		dbh.authenticate(MONGO_USER,MONGO_PWD)
		doc_table=dbh.doc.find({})
		for row in doc_table:
			temp_doc=row
			# temp_doc['skills_set']=[]
			temp_doc['skills_name_list']=""
			doc_skill_ids=dbh.doc_skills.find_one({'id':int(row['id'])})['skills']
			for skill_id in doc_skill_ids:
				if temp_doc['skills_name_list']!="":
					temp_doc['skills_name_list']+=','
				skill_name=dbh.skills.find_one({'id':int(skill_id)})['name']
				temp_doc['skills_name_list']+=skill_name
				# temp_doc['skills_set'].append(temp_skill_set)

			doc_list.append(temp_doc)
	except ConnectionFailure, e:
		sys.stderr.write("Could not connect to MongoDB: %s" % e)
	return render_template('seekho.html',doc_list=doc_list)


app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__=='__main__':
	app.debug = True
	app.run(host='0.0.0.0')
	# app.run(debug=True)