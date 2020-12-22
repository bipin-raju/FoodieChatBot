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
        budget = tracker.get_slot('budget')
        location_detail=zomato.get_location(loc, 1)
        d1 = json.loads(location_detail)
        lat=d1["location_suggestions"][0]["latitude"]
        lon=d1["location_suggestions"][0]["longitude"]
  
        cuisines_dict={'chinese':25,'mexican':73,'italian':55,'american':1,'north indian':50,'south indian':85}
        restaurant_found_count = 0        # to call the API multiples times, until 5 best restaurants in budget are not found
        search_offset = 0                # to search for next 20 restaurants in the zomato result list (max 20 rest. are received in search API)
        response=""

        # while(restaurant_found_count < 5):
        results=zomato.restaurant_search_by_rating("", lat, lon, str(cuisines_dict.get(cuisine)), search_offset)
        json_result = json.loads(results)
        if json_result['results_shown'] == 0:
            if response == "":
                response= "No restaurants found."
            else:
                response = response + "\n Only these restaurants were found."
            #break;
        else:
            print("Restaurants found in search : ")
            for restaurant in json_result['restaurants']:
                restaurant_budget = restaurant['restaurant']['average_cost_for_two']
                print(restaurant_budget)
                if((budget == 'low'and restaurant_budget < 300) or (budget == 'mid'and restaurant_budget>=300 and restaurant_budget < 700) or (budget == 'high'and restaurant_budget >= 700)):
                    restaurant_found_count = restaurant_found_count + 1
                    response=response + " --> "+restaurant['restaurant']['name']+ " in "+ restaurant['restaurant']['location']['address']+ " has been rated " + restaurant['restaurant']['user_rating']['aggregate_rating'] + "\n"
                    if(restaurant_found_count >= 5 or search_offset >= 100):
                        break;
            search_offset = search_offset+20    # call search API for next 20 restaurants        

        if response == "":
            response= "No restaurants found."
        dispatcher.utter_message("------------------------\n"+response)
        print("Done")
        return [SlotSet('location',loc)]


class ActionValidateLocation(Action):
    def name(self):
        return 'action_validate_location'

    def run(self, dispatcher, tracker, domain):
        loc = tracker.get_slot('location')
        print('Location entity found : ' + loc)
        cities=['Ahmedabad','Bengaluru','Chennai','Delhi','Hyderabad','Kolkata','Mumbai','Pune','Agra','Ajmer','Aligarh','Amravati','Amritsar','Asansol','Aurangabad','Bareilly','Belgaum','Bhavnagar','Bhiwandi','Bhopal','Bhubaneswar','Bikaner','Bilaspur','Bokaro Steel City','Chandigarh','Coimbatore','Cuttack','Dehradun','Dhanbad','Bhilai','Durgapur','Dindigul','Erode','Faridabad','Firozabad','Ghaziabad','Gorakhpur','Gulbarga','Guntur','Gwalior','Gurgaon','Guwahati','Hamirpur','Hubli–Dharwad','Indore','Jabalpur','Jaipur','Jalandhar','Jammu','Jamnagar','Jamshedpur','Jhansi','Jodhpur','Kakinada','Kannur','Kanpur','Karnal','Kochi','Kolhapur','Kollam','Kozhikode','Kurnool','Ludhiana','Lucknow','Madurai','Malappuram','Mathura','Mangalore','Meerut','Moradabad','Mysore','Nagpur','Nanded','Nashik','Nellore','Noida','Patna','Pondicherry','Purulia','Prayagraj','Raipur','Rajkot','Rajahmundry','Ranchi','Rourkela','Salem','Sangli','Shimla','Siliguri','Solapur','Srinagar','Surat','Thanjavur','Thiruvananthapuram','Thrissur','Tiruchirappalli','Tirunelveli','Ujjain','Bijapur','Vadodara','Varanasi','Vasai-Virar City','Vijayawada','Visakhapatnam','Vellore','Warangal']
        cities_lower=[x.lower() for x in cities]
            
        if loc.lower() not in cities_lower:
            dispatcher.utter_message("Sorry, we do not operate in this city. Try some other location.")
            return [SlotSet('loc_avl', False)]
        else:
            return [SlotSet('loc_avl', True)]


class ActionValidateCuisine(Action):
    def name(self):
        return 'action_validate_cuisine'

    def cuisine_list(self):
        return["chinese","mexican","italian","american","south indian","north indian"]

    def run(self, dispatcher, tracker, domain):
        csn = tracker.get_slot('cuisine')
        print('cuisine entity found : ' + csn)
        if csn == None or csn.lower() not in self.cuisine_list():
            dispatcher.utter_message("Please enter valid cuisine from the given list.")
            return [SlotSet('csn_avl', False)]
        else:
            return [SlotSet('csn_avl', True)]


class ActionValidateBudget(Action):
    def name(self):
        return 'action_validate_budget'

    def budget_list(self):
        return["low","mid","high"]

    def run(self, dispatcher, tracker, domain):
        prc = tracker.get_slot('budget')
        print('budget entity found : ' + prc)
        if prc == None or prc.lower() not in self.budget_list():
            dispatcher.utter_message("Please enter valid budget range from the given list.")
            return [SlotSet('bgt_avl', False)]
        else:
            return [SlotSet('bgt_avl', True)]
    

class ActionSlotReset(Action):  
    def name(self):         
        return 'action_slot_reset' 
    def run(self, dispatcher, tracker, domain):         
        return[AllSlotsReset()]		
