# DiversiFind
### Support female-owned, minority-owned, and veteran-owned local businesses
## 🔍 What Inspired Us
The pandemic has been hard on local business, especially female-owned businesses and minority-owned businesses. We wanted to find a way to help these businesses, but realized it can be difficult to find out who the owners are of certain businesses without visiting them in person. So, we built DiversiFind, a Flask app to connect consumers with female-owned, minority-owned, and veteran-owned local businesses!
## 🔍 What It Does
The user can search any city along with the type of business and the identity of the business owners to get information on nearby businesses. The businesses are displayed in a nifty results page where users can click on the business to learn more or can save their favorite businesses. Our web app has an account feature where the user can create an account and log in. That way, the businesses they add to their favorites will be saved for future reference, and are neatly displayed in the favorites page.
 
## 🔍 What We Learned
### Python Flask
Although we have used Flask before, there is **always** more to learn. We learned a lot about routing and POST versus GET requests. Additionally, we learned how to call Flask functions without reloading the page, allowing for the “Favorites” feature in our web app.
### APIs
This was our first time using the SAM API which allowed us to make a request and find women-owned, minority-owned, and veteran-owned businesses in close proximity.
### Web Development
We improved our CSS, HTML, and Javascript knowledge and learned how to implement various features. We explored the Bootstrap framework and specifically how to override certain elements of bootstrap to be replaced with our own styling. 
### SQL
This was our first time ever using a SQLite database. We learned how to implement databases with Flask, as well as the syntax for making SQL queries by utilizing the `sqlite3` Python module.
## 🔍 How We Built It
### Python Flask
Flask handled the back-end of the project. We used Flask to communicate with APIs, organize data, dynamically generate content, connect to the database, and handle account logins.
### Bootstrap
Most of our front-end was designed with Bootstrap.
### SAM API
SAM API gathers woman-owned, minority-owned, and veteran-owned businesses based on the user's input city.
### Google Places API
We used the Google Places Search API refines the business list by category, and gathers additional information for each location, such as reviews and photos. Additionally, we used the Google Places Details API to get more in-depth information for each business. 
### SQL and SQLite
We used two SQLite databases-- one to handle usernames and hashed passwords, and the other to manage user favorites. SQL allowed us to make queries to the databases.
### Google App Engine
We used Google Cloud’s Google App Engine to host our Flask application and configure our domain.
###  bcrypt
bcrypt is a Python library that we used to salt and hash user passwords in order for more secure password storage.
## 🔍 Challenges
Our first challenge was finding APIs to use. Not many APIs contain details of business-owners. After searching, we were able to find the SAM API which contained fascinating information about government-registered businesses. However, halfway through the hackathon the API shutdown for maintenance. We scrambled to find an alternative, but luckily, the SAM API came back online within a few hours and we were able to resume work on our project. That’s what we get for using a government API!
Another challenge we faced was handling the SQLite database. We were both pretty inexperienced with SQL so we had to do a lot of Googling and looking at documentation, but by the end we managed to figure out how to properly interact with the database and make some pretty complicated queries. We also had issues deciding what information needed to be stored in our database which led us to recreate the database more times than we can count.
Keeping track of whether the user is logged on presented another challenge. This cannot be done with a simple variable since variables are lost as the user navigates between pages and reloads. Eventually, we discovered we could keep track of whether or not the user was logged in with session cookies. The session cookies could keep track of the username and whether or not the user logged on, which was exactly what we were looking for!
The final challenge was implementing the favoriting system. This required us to figure out how to call a Flask function without reloading the page each time. After researching various solutions, we stumbled upon using jQuery and AJAX to make the POST request.
 
## 🔍 What We’re Proud Of
We poured our hearts into this project, and it was absolutely worth it! We are thrilled with how functional the search feature is and how easy it is to use! We also love the account feature because it is straight-forward and professionally executed! It feels amazing to solve a problem we face and create something we can actually use.
## 🔍 What’s Next for DiversiFind
- Speed up the search process and find a way to make it more efficient
- Allow for more specific search location, such as search by address
- Display more details about business owners
