from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from database import connector
#from server import db, engine
from model import entities

db = connector.Manager()
engine = db.createEngine()

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        db_session = db.getSession(engine)

        user = db_session.query(entities.User
                                    ).filter(entities.User.username == username.data
                                             ).first()
        if user:
            raise ValidationError('Username already exist. Choose another')


    def validate_email(self, email):
        db_session = db.getSession(engine)

        user = db_session.query(entities.User
                                   ).filter(entities.User.email == email.data
                                             ).first()
        if user:
            raise ValidationError('Email already exist. Choose another')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Update')

    def validate_username(self, username):
        db_session = db.getSession(engine)

        if username.data != current_user.username:
            user = db_session.query(entities.User
                                        ).filter(entities.User.username == username.data
                                                 ).first()
            if user:
                raise ValidationError('Username already exist. Choose another')

    def validate_email(self, email):
        db_session = db.getSession(engine)

        if email.data != current_user.email:
            user = db_session.query(entities.User
                                       ).filter(entities.User.email == email.data
                                                 ).first()
            if user:
                raise ValidationError('Email already exist. Choose another')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')
