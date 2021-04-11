from flask import Flask, render_template, request, redirect, url_for, session
from scripts import script
import sqlite3
import os
import bcrypt
from os.path import join, dirname
from dotenv import load_dotenv
import re
from flask_sslify import SSLify

#initialize env file
dotenv_path = join(dirname(__file__), 'scripts/.env')
load_dotenv(dotenv_path)

#create Flask app
app = Flask(__name__)
sslify = SSLify(app)
app.secret_key = os.environ.get('SECRET_KEY')

#create database
db = sqlite3.connect('flask.db') # flask.db is the filename
cursor = db.cursor() # create a cursor object

# create a table to store the users
cursor.execute('CREATE TABLE IF NOT EXISTS users ( ID INTEGER PRIMARY KEY AUTOINCREMENT, USER TEXT NOT NULL, PASS TEXT NOT NULL)')

# create a table to store the user favorites
cursor.execute('CREATE TABLE IF NOT EXISTS favs ( ID INTEGER PRIMARY KEY AUTOINCREMENT, USER TEXT NOT NULL, FAV TEXT NOT NULL, ZIP TEXT NOT NULL, ADDR TEXT, CAT TEXT,PLACE TEXT)')

db.commit() # save changes
db.close()

#sql helper function. interprets sql commands
def sql(cmd, vals=None):
    conn = sqlite3.connect('flask.db')
    cur = conn.cursor()
    res = cur.execute(cmd, vals).fetchall()
    conn.commit()
    conn.close()
    return res

#home page
@app.route('/')
def index():
	return render_template('index.html')

#login page
@app.route('/login', methods = ["POST", "GET"])
def login():

  #if login form was submitted, a post request is used
  if request.method == 'POST' and 'username' in request.form and 'password' in request.form:

    #gets password for username
    pas = sql('SELECT PASS FROM users WHERE USER = ?', (
      request.form['username'],
    ))

    # If account exists in accounts table  and password matches the hash
    if len(pas)>0 and bcrypt.checkpw(request.form["password"].encode(encoding='UTF-8'), pas[0][0]):
      # Create session cookie, we can access this data in other routes
      session['loggedin'] = True
      session['user'] = request.form['username']
      return render_template('index.html')
    else:
      # Account doesnt exist or username/password incorrect
      return render_template('login.html', msg=True)

  #default login form through get request
  if request.method =="GET":
    return render_template('login.html', msg=False)

#sign up page
@app.route("/sign-up", methods=["POST", "GET"])
def signUp():
  #if sign up form was submitted, a post request is used
  if request.method=="POST":
    #checks for users with chosen username
    exist = sql('SELECT ID FROM users WHERE USER = ?', (
      request.form['username'],
    ))

    # exist should be empty if no user exists with that username
    if exist == []:

      sql('INSERT INTO users (USER, PASS) VALUES (?, ?)', (
          request.form['username'], bcrypt.hashpw(request.form["password"].encode(encoding='UTF-8'), bcrypt.gensalt()),#hashes password with salt
      ))
      #after succesfully created an acct, the user is redirected to login page
      return render_template("login.html", msg=False)
    else:
      #if error, directed back to sign up page with error msg set to True
      return render_template("sign-up.html", msg=True)
  #default sign up form through get request
  elif request.method=="GET":
    return render_template("sign-up.html", msg=False)


# routes to the search results
@app.route('/results', methods = ["POST"])
def search_results():
  if request.method== "POST":

    # creates a list of all of the filters the user specified in their search
    filters = []
    if "minority" in request.form:
      filters.append(request.form["minority"])
    if "woman" in request.form:
      filters.append(request.form["woman"])
    if "veteran" in request.form:
      filters.append(request.form["veteran"])

    # if the user did not specify which filters they want, adds all of them
    if filters==[]:
      filters = ["minorityOwned", "womanOwned", "veteranOwned"]

    # creates a list of all of the category filters the user specified in their search
    filterCategories = []
    if "arts" in request.form:
      filterCategories.append(request.form["arts"])
    if "food" in request.form:
      filterCategories.append(request.form["food"])
    if "outdoors" in request.form:
      filterCategories.append(request.form["outdoors"])
    if "professional" in request.form:
      filterCategories.append(request.form["professional"])
    if "shop" in request.form:
      filterCategories.append(request.form["shop"])
    if "travel" in request.form:
      filterCategories.append(request.form["travel"])

    # if the user did not specify which category filters they want, adds all of them
    if filterCategories==[]:
      filterCategories = ["Arts & Entertainment", "Food", "Outdoors & Recreation", "Professional & Other Places", "Shop & Service", "Travel & Transport"]
    filterCategorieStr = ", ".join(filterCategories)

    # creates a pretty version of the filters by comma seperating the list and removing the camel case
    filterStr = ", ".join(filters)
    filterStr = re.sub(r'(?<!^)(?=[A-Z])', ' ', filterStr).title()

    # finds all of the user's liked businesses in case one of them is in the search results and needs to be purple to indicate it has already been liked
    likedList = []
    if "loggedin" in session:
      likedList = sql('SELECT FAV, ZIP from favs where USER = ?', (
          session['user'],
      ))
      newLikedList = []
      for bus in likedList:
        newLikedList.append(bus[0])
      likedList = newLikedList

    # calls the Sam API to get businesses in the city specified with the specified filters
    businesses = script.getSam(request.form["city"], filters)

    # calls the Google Places API to get the businesses from the list Sam API generated that fit the specified category filters
    businesses = script.getGoogle(businesses, filterCategories)

    # beautifies the categoires
    for b in businesses:
      b["categoryStr"] = ", ".join(b["categories"])

  # renders the result page with the following variables
  return render_template("results.html", filterStr=filterStr, filterCategorieStr = filterCategorieStr, businesses = businesses, city=request.form["city"], likedList=likedList)

#logout function
@app.route('/logout')
def logout():
  #removes session cookies that were keeping the user logged in
  session.pop('loggedin', None)
  session.pop('user', None)
  #redirects to home page
  return redirect(url_for('index'))

#like function for heart button on search results page
@app.route('/like', methods=["POST"])
def like():
  #should only work if logged on and if its a post request
  if request.method=="POST" and session['loggedin']:
    #add business location and details to favorites database
    sql('INSERT INTO favs (USER, FAV, ZIP, ADDR, CAT, PLACE) VALUES (?, ?, ?, ?, ?, ?)', (
        session['user'], request.form.get('business'),  request.form.get('zipCode'), request.form.get('address'), request.form.get('category'), request.form.get('place_id')
    ))
  # directs back to search results
  return redirect(url_for("search_results"))

#like function for heart button on details page
@app.route('/likeDetails', methods=["POST"])
def likeDetails():
  #should only work if logged on and if its a post request
  if request.method=="POST" and session['loggedin']:
    #add business location and details to favorites database
    sql('INSERT INTO favs (USER, FAV, ZIP, ADDR, CAT, PLACE) VALUES (?, ?, ?, ?, ?, ?)', (
        session['user'], request.form.get('business'),  request.form.get('zipCode'), request.form.get('address'), request.form.get('category'), request.form.get('place_id')
    ))
  # directs back to details page
  return redirect(url_for("details", name=request.form.get('business'), zipcode=request.form.get('zipCode'),place_id=request.form.get("place_id")))

#unlike function for heart button on search results page
@app.route('/unlike', methods=["POST"])
def unlike():
  #should only work if logged on and if its a post request
  if request.method=="POST" and session['loggedin']:
    #remove business from favorites database based on user, business name and business zip code
    sql('DELETE FROM favs WHERE (USER, FAV, ZIP) = (?, ?, ?)', (
        session['user'], request.form.get('business'),  request.form.get('zipCode')
    ))
  # directs back to search results
  return redirect(url_for("search_results"))

#unlike function for heart button on details page
@app.route('/unlikeDetails', methods=["POST"])
def unlikeDetails():
  #should only work if logged on and if its a post request
  if request.method=="POST" and session['loggedin']:
    #remove business from favorites database based on user, business name and business zip code
    sql('DELETE FROM favs WHERE (USER, FAV, ZIP) = (?, ?, ?)', (
        session['user'], request.form.get('business'),  request.form.get('zipCode')
    ))
  # directs back to details page
  return redirect(url_for("details", name=request.form.get('business'), zipcode=request.form.get('zipCode'), place_id=request.form.get("place_id")))

#unlike function for heart button on favorites page (there is no like function for this page because favorites are removed when unliked)
@app.route('/unlikeFavorites', methods=["POST"])
def unlikeFavorites():
  #should only work if logged on and if its a post request
  if request.method=="POST" and session['loggedin']:
    #remove business from favorites database based on user, business name and business zip code
    sql('DELETE FROM favs WHERE (USER, FAV, ZIP) = (?, ?, ?)', (
        session['user'], request.form.get('business'),  request.form.get('zipCode')
    ))
  # directs back to favorites page
  return redirect(url_for("favorites"))

#favorites page
@app.route('/favorites', methods=["GET"])
def favorites():
  #only works if logged on
  if "loggedin" in session:
    #compiles list of liked businesses from favorites database
    likedList = sql('SELECT FAV, ZIP, ADDR, CAT, PLACE from favs where USER = ?', (
          session['user'],
      ))
    # reformats data to be more accessable
    newLikedList = likedList
    for i in range(len(likedList)):
      if likedList[i][3]!=None:
        newLikedList[i] = [likedList[i][0],likedList[i][1], likedList[i][2], likedList[i][3], likedList[i][3].split(", "), likedList[i][4]]
    #renders the favorites page using the list of liked businesses
    return render_template("favorites.html", likedList=newLikedList)
  #if not logged on then it sends you to the login page
  else:
    return redirect(url_for("login"))

#details page, takes name of business, business zip code, and business google places id in url
@app.route("/details/<name>/<zipcode>/<place_id>")
def details(name, zipcode, place_id):
  #reformats name
  name = name.replace('-', ' ')
  #makes a request to Google Places API
  googleInfo = script.getDetails(place_id)

  #categories to be removed
  catRemove = ["Point Of Interest", "Establishment"]

  #finds business categories
  categories = []
  for cat in googleInfo['result']["types"]:
    categories.append(cat.replace("_", " ").title())
  categories = [x for x in categories if x not in catRemove]
  googleCategory = ", ".join(categories)

  #sets googleName variable
  googleName = name

  #checks if info is present and if so sets variables accordingly
  if "formatted_phone_number" in googleInfo['result']:
    googlePhone = googleInfo['result']['formatted_phone_number']
  else:
    googlePhone = None

  if "formatted_address" in googleInfo['result']:
    googleLocation = googleInfo['result']['formatted_address']
  else:
    googleLocation = None
  googleZip = zipcode

  if 'rating' in googleInfo['result']:
    googleRating = googleInfo['result']['rating']
  else:
    googleRating = None

  if 'website' in googleInfo['result']:
    googleURL = googleInfo['result']['website']
  else:
    googleURL = None

  if 'reviews' in googleInfo['result'] and len(googleInfo['result']['reviews'])>0:
    googleDescription = googleInfo['result']['reviews'][0]['text']
  else:
    googleDescription = None

  if 'photos' in googleInfo['result'] and len(googleInfo['result']['photos'])>0:
    googleImage = "https://maps.googleapis.com/maps/api/place/photo?maxwidth=600&photoreference="+googleInfo['result']['photos'][0]['photo_reference']+"&key="+os.environ.get('GOOGLE_KEY')
  else:
    googleImage = None

  #if logged in, then checks if business is in favorites database
  if "loggedin" in session:
    ids = sql('SELECT ID FROM favs WHERE USER = ? AND FAV = ? AND ZIP = ?', (
          session['user'], name, zipcode
      ))
    if len(ids)>0:
      liked = True
    else:
      liked = False
  else:
    liked = False

  #creates business dictionary
  business = {
    'name':googleName,
    'image': googleImage,
    'category': googleCategory,
    'phone': googlePhone,
    'location': googleLocation,
    'rating': googleRating,
    'url': googleURL,
    'zipcode': googleZip,
    'place_id': place_id,
    'description': googleDescription,
    'businessLiked': liked
  }

  #renders template using business dictionary
  return render_template("details.html", business=business)


if __name__ == '__main__':
    # This is used when running locally. See entrypoint in app.yaml.
    app.run(host='0.0.0.0', port=8080, debug=True)
