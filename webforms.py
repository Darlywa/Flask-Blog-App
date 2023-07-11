from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField

#create a search form
class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("Submit")

#create login form
class LoginForm(FlaskForm):
    username = StringField("Username:", validators=[DataRequired()])
    password = PasswordField("Password:", validators=[DataRequired()])
    submit = SubmitField("Submit")

#create the blog post form
class PostForm(FlaskForm):
    title = StringField("Title", validators = [DataRequired()])
    author = StringField("Author")
    #content = StringField("Content", validators=[DataRequired()], widget = TextArea())
    content = CKEditorField('content', validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")

#create the user form
class UserForm(FlaskForm):
    name = StringField("Name:", validators = [DataRequired()])
    username = StringField("Username:", validators = [DataRequired()])
    email = StringField("Email:", validators= [DataRequired()])
    location = StringField("Location:")
    password_hash = PasswordField("Password:", validators=[DataRequired(), EqualTo("password_hash2", message="Passwords must match!")])
    password_hash2 = PasswordField("Confirm password:", validators=[DataRequired()])
    profile_pic = FileField("Profile Picture")
    submit = SubmitField("Submit")


#create password test form
class PasswordForm(FlaskForm):
    email = StringField("Whats your email", validators= [DataRequired()])
    password = PasswordField("Password", validators= [DataRequired()])
    submit = SubmitField("Submit")


#create the form class
class NameForm(FlaskForm):
    name = StringField("Full Name", validators= [DataRequired()])
    submit = SubmitField("Submit")
