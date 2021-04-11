from flask import Flask, render_template, request, redirect, url_for, session
from scripts import script
import sqlite3 
import os
import bcrypt
from os.path import join, dirname
from dotenv import load_dotenv
import re

dotenv_path = join(dirname(__file__), 'scripts/.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

db = sqlite3.connect('flask.db') # flask.db is the filename
cursor = db.cursor() # create a cursor object
cursor.execute('CREATE TABLE IF NOT EXISTS users ( ID INTEGER PRIMARY KEY AUTOINCREMENT, USER TEXT NOT NULL, PASS TEXT NOT NULL)')
cursor.execute('CREATE TABLE IF NOT EXISTS favs ( ID INTEGER PRIMARY KEY AUTOINCREMENT, USER TEXT NOT NULL, FAV TEXT NOT NULL, ZIP TEXT NOT NULL, ADDR TEXT, CAT TEXT,PLACE TEXT)')
db.commit() # save changes
db.close()


def sql(cmd, vals=None):
    conn = sqlite3.connect('flask.db')
    cur = conn.cursor()
    res = cur.execute(cmd, vals).fetchall()
    conn.commit()
    conn.close()
    return res

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/login', methods = ["POST", "GET"])
def login():
  
  if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
    
    pas = sql('SELECT PASS FROM users WHERE USER = ?', (
      request.form['username'],
    ))

    
    # If account exists in accounts table in out database
    if len(pas)>0 and bcrypt.checkpw(request.form["password"].encode(encoding='UTF-8'), pas[0][0]):
      # Create session data, we can access this data in other routes
      session['loggedin'] = True
      session['user'] = request.form['username']
      return render_template('index.html')
    else:
      # Account doesnt exist or username/password incorrect
      return render_template('login.html', msg=True)
    # Show the login form with message (if any)
  if request.method =="GET":
    return render_template('login.html', msg=False)

@app.route('/result')
def results():
	return render_template('results.html')

@app.route("/sign-up", methods=["POST", "GET"])
def signUp():
  if request.method=="POST":
    exist = sql('SELECT ID FROM users WHERE USER = ?', (
      request.form['username'],
    ))
    if exist == []:
      sql('INSERT INTO users (USER, PASS) VALUES (?, ?)', (
          request.form['username'],
          bcrypt.hashpw(request.form["password"].encode(encoding='UTF-8'), bcrypt.gensalt()),
      ))
      return render_template("login.html", msg=False)
    else:
      return render_template("sign-up.html", msg=True)
  elif request.method=="GET":
    return render_template("sign-up.html", msg=False)


@app.route('/results', methods = ["POST"])
def search_results():
  if request.method== "POST":
    filters = []
    if "minority" in request.form:
      filters.append(request.form["minority"])
    if "woman" in request.form:
      filters.append(request.form["woman"])
    if "veteran" in request.form:
      filters.append(request.form["veteran"])

    if filters==[]:
      filters = ["minorityOwned", "womanOwned", "veteranOwned"]

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

    if filterCategories==[]:
      filterCategories = ["Arts & Entertainment", "Food", "Outdoors & Recreation", "Professional & Other Places", "Shop & Service", "Travel & Transport"]
    filterCategorieStr = ", ".join(filterCategories)

    filterStr = ", ".join(filters)
    filterStr = re.sub(r'(?<!^)(?=[A-Z])', ' ', filterStr).title()

    likedList = []
    if "loggedin" in session:
      likedList = sql('SELECT FAV, ZIP from favs where USER = ?', (
          session['user'],
      ))
      newLikedList = []
      for bus in likedList:
        newLikedList.append(bus[0])
      likedList = newLikedList
    businesses = script.getSam(request.form["city"], filters)
    businesses = script.getGoogle(businesses, filterCategories)

    for b in businesses:
      b["categoryStr"] = ", ".join(b["categories"])

  return render_template("results.html", filterStr=filterStr, filterCategorieStr = filterCategorieStr, businesses = businesses, city=request.form["city"], likedList=likedList)

@app.route('/logout')
def logout():
  session.pop('loggedin', None)
  session.pop('user', None)
  return redirect(url_for('index'))

@app.route('/like', methods=["POST"])
def like():
  if request.method=="POST" and session['loggedin']:
    sql('INSERT INTO favs (USER, FAV, ZIP, ADDR, CAT, PLACE) VALUES (?, ?, ?, ?, ?, ?)', (
        session['user'], request.form.get('business'),  request.form.get('zipCode'), request.form.get('address'), request.form.get('category'), request.form.get('place_id')
    ))
  return redirect(url_for("search_results"))

@app.route('/likeDetails', methods=["POST"])
def likeDetails():
  if request.method=="POST" and session['loggedin']:
    sql('INSERT INTO favs (USER, FAV, ZIP, ADDR, CAT, PLACE) VALUES (?, ?, ?, ?, ?, ?)', (
        session['user'], request.form.get('business'),  request.form.get('zipCode'), request.form.get('address'), request.form.get('category'), request.form.get('place_id')
    ))
  return redirect(url_for("details", name=request.form.get('business'), zipcode=request.form.get('zipCode'),place_id=request.form.get("place_id")))

@app.route('/unlike', methods=["POST"])
def unlike():
  if request.method=="POST" and session['loggedin']:
    sql('DELETE FROM favs WHERE (USER, FAV, ZIP) = (?, ?, ?)', (
        session['user'], request.form.get('business'),  request.form.get('zipCode')
    ))
  return redirect(url_for("search_results"))

@app.route('/unlikeDetails', methods=["POST"])
def unlikeDetails():
  if request.method=="POST" and session['loggedin']:
    sql('DELETE FROM favs WHERE (USER, FAV, ZIP) = (?, ?, ?)', (
        session['user'], request.form.get('business'),  request.form.get('zipCode')
    ))
  return redirect(url_for("details", name=request.form.get('business'), zipcode=request.form.get('zipCode'), place_id=request.form.get("place_id")))

@app.route('/unlikeFavorites', methods=["POST"])
def unlikeFavorites():
  if request.method=="POST" and session['loggedin']:
    sql('DELETE FROM favs WHERE (USER, FAV, ZIP) = (?, ?, ?)', (
        session['user'], request.form.get('business'),  request.form.get('zipCode')
    ))
  return redirect(url_for("favorites"))

@app.route('/favorites', methods=["GET"])
def favorites():
  if "loggedin" in session:
    likedList = sql('SELECT FAV, ZIP, ADDR, CAT, PLACE from favs where USER = ?', (
          session['user'],
      ))

    newLikedList = likedList
    for i in range(len(likedList)):
      if likedList[i][3]!=None:
        newLikedList[i] = [likedList[i][0],likedList[i][1], likedList[i][2], likedList[i][3], likedList[i][3].split(", "), likedList[i][4]]
    return render_template("favorites.html", likedList=newLikedList)
  else:
    return redirect(url_for("login"))

@app.route("/details/<name>/<zipcode>/<place_id>")
def details(name, zipcode, place_id):
  name = name.replace('-', ' ')
  googleInfo = script.getDetails(place_id)

  catRemove = ["Point Of Interest", "Establishment"]
  
  categories = []
  for cat in googleInfo['result']["types"]:
    categories.append(cat.replace("_", " ").title())
  categories = [x for x in categories if x not in catRemove]
  googleCategory = ", ".join(categories)

  googleName = name

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
    googleImage = "https://maps.googleapis.com/maps/api/place/photo?maxheight=600&photoreference="+googleInfo['result']['photos'][0]['photo_reference']+"&key="+os.environ.get('GOOGLE_KEY')
  else:
    googleImage = None
    

  if "loggedin" in session:
    ids = sql('SELECT ID from favs where (USER, FAV, ZIP) = (?,?,?) ', (
          session['user'], name, zipcode
      ))
    if len(ids)>0:
      liked = True
    else: 
      liked = False
  else:
    liked = False

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
  
  return render_template("details.html", business=business)



app.run(host='0.0.0.0', port=8080)