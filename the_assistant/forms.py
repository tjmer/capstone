from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.fields.core import IntegerField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from the_assistant.models import User
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2,max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2,max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField("Update Profile Picture", validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

class CreateCharacter(FlaskForm):
    character_name = StringField('Name', validators=[DataRequired()])
    total_health = IntegerField('Health', validators=[DataRequired()])
    current_health = IntegerField('Current Health', validators=[DataRequired()])
    ac = IntegerField('Armor-Class', validators=[DataRequired()])
    strength = IntegerField('Str', validators=[DataRequired()])
    dexterity = IntegerField('Dex', validators=[DataRequired()])
    constition = IntegerField('Const', validators=[DataRequired()])
    intelligence = IntegerField('Int',  validators=[DataRequired()])
    wisdom = IntegerField('Wis', validators=[DataRequired()])
    charisma = IntegerField('Char', validators=[DataRequired()])
    bio = TextAreaField('Character Bio', validators=[DataRequired()])
    submit = SubmitField('Submit')

class CreateMonster(FlaskForm):
    monster_name = StringField('Name', validators=[DataRequired()])
    total_hp = IntegerField('Health', validators=[DataRequired()])
    current_hp = IntegerField('Current Health', validators=[DataRequired()])
    monster_desc = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit')

class CreateShop(FlaskForm):
    shop_name = StringField('Name', validators=[DataRequired()])
    shop_owner = StringField('Owner', validators=[DataRequired()])
    inventory = TextAreaField('Inventory', validators=[DataRequired()])
    submit = SubmitField('Submit')