import requests
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

categories = {
  "Arts & Entertainment": ['Amusement Park', 'Aquarium', 'Art Gallery', 'Bowling Alley', 'Casino', 'Movie Theater', 'Museum', 'Night Club', 'Stadium', 'Zoo', 'Tourist Attraction'],

  "Food": ['Bakery', 'Bar', 'Cafe', 'Restaurant', 'Food'],

  "Outdoors & Recreation": ['Campground', 'Cemetery', 'Park'],

  "Professional & Other Places": ['Accounting', 'Church', 'Club House', 'Dentist', 'Electrician', 'Doctor', 'Fire Station', 'Funeral Home', 'Hindu Temple', 'Hospital', 'Library', 'Mosque', 'Painter', 'Parking', 'Post Office', 'Physiotherapist', 'Plumber', 'Police', 'Roofing Contractor', 'Storage', 'Synagogue', 'School'],

  "Shop & Service": ['ATM', 'Bank', 'Beauty Salon', 'Bicycle Store', 'Book Store', 'Car Dealer', 'Car Repair', 'Car Wash', 'Clothing Store', 'Convenience Store', 'Drugstore', 'Department Store', 'Electronics Store', 'Florist', 'Furniture Store', 'Gas Station', 'Gym', 'Hair Care', 'Hardware Store', 'Home Goods Store', 'Insurance Agency', 'Jewelry Store', 'Laundry', 'Lawyer', 'Liquor Store', 'Locksmith', 'Lodging', 'Meal Delivery', 'Meal Takeaway', 'Movie Rental', 'Moving Company', 'Pet Store', 'Pharmacy', 'Real Estate Agency', 'Shoe Store', 'Shopping Mall', 'Spa', 'Store', 'Supermarket'],

  "Travel & Transport": ['Airport', 'Bus Station', 'Light Rail Station', 'Subway Station', 'Taxi Stand', 'Train Station', 'Transit Station', 'Travel Agency']


}

catRemove = ["Point Of Interest", "Establishment"]

def getSam(city, filters):
  if len(filters) != 0:
    filters = '+AND+('+':true)+OR+('.join([str(elem) for elem in filters]) +':true)'
  else: 
    filters = ''
    
  samP = {
    'qterms':f'(samAddress.city:{city}){filters}',
    'api_key': os.environ.get('SAM_API'),
    'start':1,
    'length':100
  }

  response = requests.get('https://api.data.gov/sam/v3/registrations', params=samP)

  businesses = []

  for business in response.json()['results']:
    businesses.append(
      { 'name': business['legalBusinessName'],
        'nameURL': business['legalBusinessName'].replace(" ", "-").replace("'", ""),
        'zip': business['samAddress']['zip']
      })
  
  return businesses

def getGoogle(businesses, filters):
  for i in range(len(businesses)-1,-1,-1):
    business = businesses[i]

    search = {
      'query': business['name'] + " " + business['zip'],
      'key': os.environ.get('GOOGLE_KEY')
    }
    try:
      response = requests.get("https://maps.googleapis.com/maps/api/place/textsearch/json", params = search)

      venue = response.json()["results"][0]
      business["place_id"] = venue["place_id"]

      business["categories"] = []
        
      for cat in venue["types"]:
          business["categories"].append(cat.replace("_", " ").title())
      business["categories"] = [x for x in business["categories"] if x not in catRemove]
      business["address"] = venue["formatted_address"]
    
      for n in filters:
        for m in business["categories"]:
          if m in categories.get(n):
            business["type"] = n
      if business["type"] == "":
        businesses.pop(i)

    except:
      businesses.pop(i)
  return businesses
    

def getDetails(place_id):

  search = {
    'place_id': place_id,
    'key': os.environ.get('GOOGLE_KEY')
  }

  response = requests.get('https://maps.googleapis.com/maps/api/place/details/json', params=search)
  return response.json()
