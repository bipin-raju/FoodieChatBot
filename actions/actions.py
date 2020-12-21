from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_sdk import Action
from rasa_sdk.events import SlotSet
import actions.zomatopy
import json

class ActionSearchRestaurants(Action):
	def name(self):
		return 'action_search_restaurants'
		
	def run(self, dispatcher, tracker, domain):
		config={ "user_key":"21819872aa99eeb0d81ccfdaa2f423fe"} #"f4924dc9ad672ee8c4f8c84743301af5"}
		zomato = actions.zomatopy.initialize_app(config)
		loc = tracker.get_slot('location')
		cuisine = tracker.get_slot('cuisine')
		# budget = 3
		budget = tracker.get_slot('budget')
		print(budget)
		location_detail=zomato.get_location(loc, 1)
		d1 = json.loads(location_detail)
		lat=d1["location_suggestions"][0]["latitude"]
		lon=d1["location_suggestions"][0]["longitude"]
  
		cuisines_dict={'chinese':25,'mexican':73,'italian':55,'american':1,'north indian':50,'south indian':85}
		restaurant_found_count = 0		# to call the API multiples times, until 5 best restaurants in budget are not found
		search_offset = 0				# to search for next 20 restaurants in the zomato result list (max 20 rest. are received in search API)
		response=""

		while(restaurant_found_count < 5):
			results=zomato.restaurant_search_by_rating("", lat, lon, str(cuisines_dict.get(cuisine)), search_offset)
			json_result = json.loads(results)
			if json_result['results_shown'] == 0:
				if response == "":
					response= "no results"
				else:
					response = response + "\n Only these restaurants were found."
				break;
			else:
				print("Restaurants found in search : ")
				for restaurant in json_result['restaurants']:
					restaurant_budget = restaurant['restaurant']['average_cost_for_two']
					print(restaurant_budget)
					if((budget == 'low' and restaurant_budget < 300) or (budget == 'mid' and restaurant_budget>=300 and restaurant_budget < 700) or (budget == 'high' and restaurant_budget >= 700)):
						restaurant_found_count = restaurant_found_count + 1
						response=response+ restaurant['restaurant']['name']+ " in "+ restaurant['restaurant']['location']['address']+ " has been rated " + restaurant['restaurant']['user_rating']['aggregate_rating'] + "\n"
						if(restaurant_found_count >= 5 or search_offset >= 100):
							break;
				search_offset = search_offset+20	# call search API for next 20 restaurants		
  
		dispatcher.utter_message("------------------------\n"+response)
		print("Done")
		return [SlotSet('location',loc)]

