import httplib2
import requests
import json
import random
import string

from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash, make_response
from flask import session as login_session
from models import Base, User, Category, Item
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

engine = create_engine('sqlite:////var/www/catalog_app/db/catalog.db',
    connect_args={'check_same_thread': False})
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

CLIENT_ID = json.loads(
    open('/var/www/catalog_app/client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"
app.config['APPLICATION_ROOT'] = '/catalog_app'
app.secret_key = 'qexcvb;ityz;fgx65437vbljhlgjkhwe32txvcbflkiwertl;jh25'

# The main page
@app.route('/')
def showMain():
    categories = session.query(Category).all()
    return render_template('main.html', categories=categories)


# List a category's items
@app.route('/catalog/<string:cat>/items')
def showItems(cat):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name=cat).one()
    items = session.query(Item).filter_by(category_id=category.id)
    return render_template('main.html', categories=categories,
                           category=category, items=items)


# Show one item and it's description.
@app.route('/catalog/<string:cat>/<string:item>')
def showItem(cat, item):
    category = session.query(Category).filter_by(name=cat).one()
    item = session.query(Item).filter_by(name=item, category=category).one()
    return render_template('item.html', category=category, item=item)


# Add a new item
@app.route('/catalog_app/catalog/<string:cat>/add', methods=['GET', 'POST'])
def addItem(cat):
    if 'email' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(name=cat).one()
    if request.method == 'POST':
        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       category=category,
                       user_id=login_session['user_id'])
        session.add(newItem)
        flash('%s created' % newItem.name)
        session.commit()
        return redirect(url_for('showItems', cat=category.name))
    else:
        return render_template('additem.html', category=category)


# Delete an item, only if the user matches the owner
@app.route('/catalog/<string:cat>/<string:item>/delete',
           methods=['GET', 'POST'])
def deleteItem(cat, item):
    if 'email' not in login_session:
        return redirect('/login')
    if item.user_id != login_session['user_id']:
        return "You're not the owner of this item."
    category = session.query(Category).filter_by(name=cat).one()
    item = session.query(Item).filter_by(name=item, category=category).one()
    if request.method == 'POST':
        session.delete(item)
        flash('%s deleted' % item.name)
        session.commit()
        return redirect(url_for('showItems', cat=category.name))
    else:
        return render_template('deleteitem.html', cat=category, item=item)


# Edit the item, only if the user matches the owner
@app.route('/catalog/<string:cat>/<string:item>/edit',
           methods=['GET', 'POST'])
def editItem(cat, item):
    if 'email' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(name=cat).one()
    item = session.query(Item).filter_by(name=item, category=category).one()
    if item.user_id != login_session['user_id']:
        return "You're not the owner of this item."
    if request.method == 'POST':
        item.name = request.form['name']
        item.description = request.form['description']
        session.add(item)
        flash('%s updated' % item.name)
        session.commit()
        return redirect(url_for('showItems', cat=category.name))
    else:
        return render_template('edititem.html', cat=category, item=item)


# JSON of the whole catalog
@app.route('/catalog.json')
def catalogJSON():
    categories = session.query(Category).all()

    list = {'Categories': []}
    for c in categories:
        category_list = {'id': c.id, 'name': c.name, 'items': []}
        items = session.query(Item).filter_by(category_id=c.id)
        for i in items:
            category_list['items'].append(i.serialize)
        list['Categories'].append(category_list)

    response = make_response(json.dumps(list, indent=4))
    response.headers['Content-Type'] = 'application/json'
    return response


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code, now compatible with Python3
    request.get_data()
    code = request.data.decode('utf-8')

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    # Submit request, parse response - Python3 compatible
    h = httplib2.Http()
    response = h.request(url, 'GET')[1]
    str_response = response.decode('utf-8')
    result = json.loads(str_response)

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
                                 'Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    print data

    login_session['name'] = data['name']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['name']
    output += '</h1>'
    flash("%s logged in" % login_session['email'])
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['name'], email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        flash("%s logged out" % login_session['email'])
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['name']
        del login_session['email']
        del login_session['user_id']
        
        return redirect('/')
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# launch web server
if __name__ == '__main__':
    app.secret_key = 'qexcvb;ityz;fgx65437vbljhlgjkhwe32txvcbflkiwertl;jh25'
    app.debug = True
    app.run()
