# dependencies
import sys
import os
from flask import Flask, redirect, url_for, flash, render_template, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.contrib.fixers import ProxyFix
from sqlalchemy.orm.exc import NoResultFound
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from flask_dance.consumer.backend.sqla import OAuthConsumerMixin, SQLAlchemyBackend
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_login import (LoginManager, UserMixin, current_user, login_required, login_user, logout_user)
from wtforms import Form, PasswordField, StringField, validators, SubmitField
from models import *

def read_secret():
    with open('api_secret.txt', 'r') as f:
        return [i.strip() for i in f.readlines()]

app = Flask(__name__)
app.debug = True
app.config.from_object('config.DevelopmentConfig')
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app.wsgi_app = ProxyFix(app.wsgi_app)
blueprint = make_facebook_blueprint(
    client_id=read_secret()[0],
    client_secret=read_secret()[1],
)
app.register_blueprint(blueprint, url_prefix="/login_oauth", base_url="https://graph.facebook.com/", authorization_url="https://www.facebook.com/dialog/oauth", token_url="https://graph.facebook.com/oauth/access_token")


login_manager = LoginManager()
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# setup SQLAlchemy backend
blueprint.backend = SQLAlchemyBackend(OAuth, db.session, user=current_user)

def render_nav(user_auth):
    pagesDict = {'index':'Home','about':'About','contact':'Contact','media_share':'Media'}
    pages = ['index', 'about', 'contact']
    fname = None
    if user_auth:
        pages.append('media_share')
        fname = current_user.name.split(' ')
        if len(fname) > 1:
            fname = fname[0] + ' ' + ''.join(c for c in fname[1] if c.isupper()) + '.'
        else:
            fname = fname[0]
    return [pages, pagesDict, fname]

# create/login local user on successful OAuth login
@oauth_authorized.connect_via(blueprint)
def facebook_logged_in(blueprint, token):
    if not token:
        print("LMAO", file=sys.stderr)
        flash("Failed to log in with Facebook.", category="error")
        return False

    resp = blueprint.session.get("/oauth2/v2/userinfo")
    if not resp.ok:
        print("Failed to fetch user info from Facebook.", file=sys.stderr)
        msg = "Failed to fetch user info from Facebook."
        flash(msg, category="error")
        return False

    facebook_info = resp.json()
    facebook_user_id = str(facebook_info["id"])

    # Find this OAuth token in the database, or create it
    query = OAuth.query.filter_by(
        provider=blueprint.name,
        provider_user_id=facebook_user_id,
    )
    try:
        oauth = query.one()
    except NoResultFound:
        oauth = OAuth(
            provider=blueprint.name,
            provider_user_id=facebook_user_id,
            token=token,
        )

    if oauth.user:
        login_user(oauth.user)
        flash("Successfully signed in with Facebook.")

    else:
        # Create a new local user account for this user
        user = User(
            # Remember that `email` can be None, if the user declines
            # to publish their email address on Facebook!
            email=facebook_info["email"],
            name=facebook_info["name"],
        )
        # Associate the new local user account with the OAuth token
        oauth.user = user
        # Save and commit our database models
        db.session.add_all([user, oauth])
        db.session.commit()
        # Log in the new local user account
        login_user(user)
        flash("Successfully signed in with Facebook.")

    # Disable Flask-Dance's default behavior for saving the OAuth token
    return False

# notify on OAuth provider error
@oauth_error.connect_via(blueprint)
def facebook_error(blueprint, error, error_description=None, error_uri='login'):
    msg = (
        "OAuth error from {name}! "
        "error={error} description={description} uri={uri}"
    ).format(
        name=blueprint.name,
        error=error,
        description=error_description,
        uri=error_uri,
    )
    flash(msg, category="error")

@app.route('/')
def index():
    pages, pagesDict, fname = render_nav(current_user.is_authenticated)
    return render_template('index.html', pages=pages, pagesDict=pagesDict, fname=fname)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have logged out")
    return redirect(url_for('index'))

@app.errorhandler(404)
def error404(error):
    return render_template('404_error.html'), 404

@app.errorhandler(403)
def error403(error):
    return render_template('403_error.html'), 403

@app.route('/robot.txt')
def robot():
    return 'User-agent: *\nDisallow: /'

@app.route('/contact')
def contact():
    pages, pagesDict, fname = render_nav(current_user.is_authenticated)
    return render_template('contact.html', pages=pages, pagesDict=pagesDict, fname=fname)

@app.route('/about')
def about():
    pages, pagesDict, fname = render_nav(current_user.is_authenticated)
    return render_template('about.html', pages=pages, pagesDict=pagesDict, fname=fname)

class LoginForm(Form):
    username = StringField(u'Username', validators=[validators.input_required()])
    password  = PasswordField(u'Password', validators=[validators.input_required()])

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm(request.form)
    # print(form.validate(), file=sys.stderr)
    print(request.method == 'POST', file=sys.stderr)

    if current_user.is_authenticated:
        return redirect(request.args.get('next') or url_for('index'))
    # if request.method == 'POST' and form.validate():
    if request.method == 'POST':
        # Login and validate the user.
        # user should be an instance of your `User` class
        user = User.query.filter_by(username=request.form['username']).first()
        if not user:
            print('failed to log in', file=sys.stderr)
            flash('Failed to log in, check your credentials.')
        else:
            login_user(user)

            flash('Logged in successfully.')

            next = request.args.get('next')
            # is_safe_url should check if the url is safe for redirects.
            # See http://flask.pocoo.org/snippets/62/ for an example.
            # if not is_safe_url(next):
            #     return flask.abort(400)
            print('logged in', file=sys.stderr)

            return redirect(next or url_for('index'))
    return render_template('login.html', form=form)

@app.route('/media_share')
@login_required
def media_share():
    pages, pagesDict, fname = render_nav(current_user.is_authenticated)
    return render_template('mediashare.html', pages=pages, pagesDict=pagesDict, fname=fname)

db.init_app(app)
login_manager.init_app(app)

if __name__ == "__main__":
    if "--setup" in sys.argv:
        with app.app_context():
            db.create_all()
            db.session.commit()
            print("Database tables created")
    else:
        app.run(debug=True)
