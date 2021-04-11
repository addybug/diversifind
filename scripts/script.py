import requests
import os
from os.path import join, dirname
from dotenv import load_dotenv

#initialize env file
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# creates dictionary to define cateogies and topics
categories = {
  "Arts & Entertainment": ['Amusement Park', 'Aquarium', 'Art Gallery', 'Bowling Alley', 'Casino', 'Movie Theater', 'Museum', 'Night Club', 'Stadium', 'Zoo', 'Tourist Attraction'],

  "Food": ['Bakery', 'Bar', 'Cafe', 'Restaurant', 'Food'],

  "Outdoors & Recreation": ['Campground', 'Cemetery', 'Park'],

  "Professional & Other Places": ['Accounting', 'Church', 'Club House', 'Dentist', 'Electrician', 'Doctor', 'Fire Station', 'Funeral Home', 'Hindu Temple', 'Hospital', 'Library', 'Mosque', 'Painter', 'Parking', 'Post Office', 'Physiotherapist', 'Plumber', 'Police', 'Roofing Contractor', 'Storage', 'Synagogue', 'School'],

  "Shop & Service": ['ATM', 'Bank', 'Beauty Salon', 'Bicycle Store', 'Book Store', 'Car Dealer', 'Car Repair', 'Car Wash', 'Clothing Store', 'Convenience Store', 'Drugstore', 'Department Store', 'Electronics Store', 'Florist', 'Furniture Store', 'Gas Station', 'Gym', 'Hair Care', 'Hardware Store', 'Home Goods Store', 'Insurance Agency', 'Jewelry Store', 'Laundry', 'Lawyer', 'Liquor Store', 'Locksmith', 'Lodging', 'Meal Delivery', 'Meal Takeaway', 'Movie Rental', 'Moving Company', 'Pet Store', 'Pharmacy', 'Real Estate Agency', 'Shoe Store', 'Shopping Mall', 'Spa', 'Store', 'Supermarket'],

  "Travel & Transport": ['Airport', 'Bus Station', 'Light Rail Station', 'Subway Station', 'Taxi Stand', 'Train Station', 'Transit Station', 'Travel Agency']


}

# a list of meaningless categories all Google Place API responses have that needs to be removed
catRemove = ["Point Of Interest", "Establishment"]


# this function calls the Sam API:
# The SAM API is a RESTful method of retrieving public information about the businesses or individuals (referred to as “entities”) within the SAM data set.
# the reason we use the Sam API is because it has filters for women owned, minority owned, veteran owned, etc.
def getSam(city, filters):
  # creates the parameter that filters the response
  if len(filters) != 0:
    filters = '+AND+('+':true)+OR+('.join([str(elem) for elem in filters]) +':true)'
  else:
    filters = ''

  # the parameters passed into the Sam request
  samP = {
    'qterms':f'(samAddress.city:{city}){filters}',
    'api_key': os.environ.get('SAM_API'),
    'start':1,
    'length':150
  }

  # makes a request with the specified parameters
  response = requests.get('https://api.data.gov/sam/v3/registrations', params=samP)

  businesses = []

  # parses the data into a list of dictionaries
  for business in response.json()['results']:
    businesses.append(
      { 'name': business['legalBusinessName'],
        'nameURL': business['legalBusinessName'].replace(" ", "-").replace("'", ""),
        'zip': business['samAddress']['zip']
      })

  return businesses

# this function calls the Google Places Search API to categorize and filter the results based on the user's preference
# The Places API lets you search for place information using a variety of categories, including establishments, prominent points of interest, and geographic locations.
def getGoogle(businesses, filters):

  for i in range(len(businesses)-1,-1,-1):
    business = businesses[i]

    # the parameters passed into the request
    search = {
      'query': business['name'] + " " + business['zip'],
      'key': os.environ.get('GOOGLE_KEY')
    }
    try:
      # tries to make the resquest to the API and if there's no response removes the business from the list
      response = requests.get("https://maps.googleapis.com/maps/api/place/textsearch/json", params = search)

      venue = response.json()["results"][0]

      # the place id is important for getting details on the place
      business["place_id"] = venue["place_id"]

      business["categories"] = []

      # beautifies the cateogires and then parses the categories into a list
      for cat in venue["types"]:
          business["categories"].append(cat.replace("_", " ").title())
      # removes unwanted categories
      business["categories"] = [x for x in business["categories"] if x not in catRemove]
      business["address"] = venue["formatted_address"]

      # checks if the categories fit any of the user-defined preferences and removes the businesses that don't
      for n in filters:
        for m in business["categories"]:
          if m in categories.get(n):
            business["type"] = n
      if business["type"] == "":
        businesses.pop(i)

    except:
      businesses.pop(i)
  return businesses


# gets location details from the Google Places Details API
def getDetails(place_id):

  search = {
    'place_id': place_id,
    'key': os.environ.get('GOOGLE_KEY')
  }

  response = requests.get('https://maps.googleapis.com/maps/api/place/details/json', params=search)
  return response.json()
