from flask import Flask, render_template, request, Response, url_for, flash, redirect, abort
from flask_socketio import SocketIO
from flask_bcrypt import Bcrypt
from database import connector
#from flask_sqlalchemy import SQLAlchemy
from model import entities
from forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
import json

db = connector.Manager()
engine = db.createEngine()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

socketio = SocketIO(app)

@login_manager.user_loader
def load_user(user_id):
    db_session = db.getSession(engine)
    return db_session.query(entities.User).get(int(user_id))

@app.route('/')
def index():
    db_session = db.getSession(engine)
    posts = db_session.query(entities.Post
                    ).all()
    return render_template('index.html', posts = posts)

@app.route('/crud_users')
def crud_users():
    return render_template('crud_users.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        name = ""
        fullname = ""

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = entities.User(
            username=username,
            email=email,
            password=hashed_password,
            name=name,
            fullname=fullname
            )
        session = db.getSession(engine)
        session.add(user)
        session.commit()

        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('index'))

    return render_template('register.html', title='Register', form=form)

@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def newpost():
    postform = PostForm()
    user = current_user

    if postform.validate_on_submit():
        post = entities.Post(title=postform.title.data, content = postform.content.data,
                    user_id = user.id)
        session = db.getSession(engine)
        session.add(post)
        session.commit()
        #flash('your post has been created')
        return redirect(url_for('index'))

    return render_template('create_post.html', title='New Post', form=postform, legend='New Post')

@app.route("/post/<post_id>", methods=['GET'])
def post(post_id):
    session = db.getSession(engine)
    post = session.query(entities.Post).get(int(post_id))
    if post:
        return render_template('post.html', title=post.title, post=post)
    else:
        message = { 'status': 404, 'message': 'Not Found'}
        return Response(message, status=404, mimetype='application/json')

@app.route("/post/<post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    session = db.getSession(engine)
    post = session.query(entities.Post).get(int(post_id))
    user = current_user
    form = PostForm()

    if post:
        if post.user_id != user.id:
            abort(403)

        if form.validate_on_submit():
            post.title = form.title.data
            post.content = form.content.data
            session.add(post)
            session.commit()
            flash('Your post has been updated!', 'success')
            return redirect(url_for('post', post_id=post.id))
        elif request.method == 'GET':
            form.title.data = post.title
            form.content.data = post.content

        return render_template('create_post.html', title='Update post', form=form, legend='Update Post')
    else:
        message = { 'status': 404, 'message': 'Not Found'}
        return Response(message, status=404, mimetype='application/json')

@app.route("/post/<post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    session = db.getSession(engine)
    post = session.query(entities.Post).get(int(post_id))
    user = current_user
    form = PostForm()

    if post:
        if post.user_id != user.id:
            abort(403)

        session.delete(post)
        session.commit()
        flash('Your post has been delete!', 'success')
        return redirect(url_for('index'))

    else:
        message = { 'status': 404, 'message': 'Not Found'}
        return Response(message, status=404, mimetype='application/json')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        db_session = db.getSession(engine)

        try:
            user = db_session.query(entities.User
                    ).filter(entities.User.email == email
                ).one()
            if user and bcrypt.check_password_hash(user.password, password):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                #flash('You''ve been logged in!', 'success')
                return redirect(next_page) if next_page else redirect(url_for('index'))
            else:
                flash('Login Unsuccessfull. Please check username and password', 'danger')

        except Exception:
            flash('Login Unsuccessfull. Please check username and password', 'danger')

        """if form.email.data == 'admin@gmail.com' and form.password.data == '12345678':
            flash('You''ve been logged in!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessfull. Please check username and password', 'danger')"""

    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    updform = UpdateAccountForm()
    db_session = db.getSession(engine)

    if updform.validate_on_submit():
        #current_user.username = updform.username.data
        user = current_user
        user.username = updform.username.data
        user.email = updform.email.data
        db_session.add(user)
        db_session.commit()
        flash('Your account has been updated2!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        updform.username.data = current_user.username
        updform.email.data = current_user.email

    return render_template('account.html', title='Account', form=updform)


def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

#def sessions():
    #return render_template('session.html')

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)

@app.route('/create_test_users', methods = ['GET']) #TESTING
def create_test_users():
    db_session = db.getSession(engine)
    user = entities.User(username="rvmosquera", email="raulv.mosquera@gmail.com", password="12345678",
                         name="", fullname="" )
    db_session.add(user)
    db_session.commit()
    return "Test user created!"

@app.route('/users', methods = ['GET'])
def users():
    db_session = db.getSession(engine)
    users = db_session.query(entities.User)
    data = users[:]

    return Response(json.dumps(data, cls=connector.AlchemyEncoder), mimetype = 'application/json')

@app.route('/users/<id>', methods = ['GET'])
def get_user(id):
    db_session = db.getSession(engine)
    users = db_session.query(entities.User).filter(entities.User.id == id)
    for user in users:
        js = json.dumps(user, cls=connector.AlchemyEncoder)
        return  Response(js, status=200, mimetype='application/json')

    message = { 'status': 404, 'message': 'Not Found'}
    return Response(message, status=404, mimetype='application/json')

# Create
@app.route('/users', methods = ['POST'])
def create_user():
    c =  json.loads(request.form['values'])

    username = c['username']
    email=c['email']

    name=""
    if 'name' in c:
        name = c['name']

    fullname=""
    if 'fullname' in c:
        fullname = c['fullname']

    db_session = db.getSession(engine)

    user = db_session.query(entities.User
                            ).filter(entities.User.username == username).first()

    if user:
        message = 'User already exists!'
        return Response(message, status=404, mimetype='application/json')

    user = db_session.query(entities.User
                            ).filter(entities.User.email == email ).first()
    if user:
        message = 'Email already exists!'
        return Response(message, status=404, mimetype='application/json')

    user = entities.User(
        username=username,
        name=name,
        email=email,
        fullname=fullname,
        password=c['password']
    )
    session = db.getSession(engine)
    session.add(user)
    session.commit()
    return 'User Created'

# Update
@app.route('/users', methods = ['PUT'])
def update_user():
    session = db.getSession(engine)
    id = request.form['key']
    user = session.query(entities.User).filter(entities.User.id == id).first()
    c =  json.loads(request.form['values'])
    for key in c.keys():
        setattr(user, key, c[key])
    session.add(user)
    session.commit()
    return 'User Updated'

# Delete
@app.route('/users', methods = ['DELETE'])
def delete_user():
    id = request.form['key']
    session = db.getSession(engine)
    users = session.query(entities.User).filter(entities.User.id == id)
    for user in users:
        session.delete(user)
    session.commit()
    return "User Deleted"

if __name__ == '__main__':
    socketio.run(app, debug=True)


