from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_sdk import Action
from rasa_sdk.events import SlotSet
from rasa_sdk.events import AllSlotsReset
import actions.zomatopy
import send_mail
import pandas as pd
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

        # keep experiencing time-out error due to multiple API calls
        # while(restaurant_found_count < 5 and search_offset < 100):
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
                if((budget == 'low'and restaurant_budget < 300) or (budget == 'mid'and restaurant_budget>=300 and restaurant_budget <= 700) or (budget == 'high'and restaurant_budget > 700)):
                    restaurant_found_count = restaurant_found_count + 1
                    response=response + " --> "+restaurant['restaurant']['name']+ " in "+ restaurant['restaurant']['location']['address']+ " has been rated " + restaurant['restaurant']['user_rating']['aggregate_rating'] + "\n"
                if(restaurant_found_count >= 5):
                    break;
            # search_offset = search_offset+20    # call search API for next 20 restaurants        

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


class ActionSendEmail(Action):  
    def name(self):         
        return 'action_send_email' 
    def run(self, dispatcher, tracker, domain):         
        config={ "user_key":"21819872aa99eeb0d81ccfdaa2f423fe"} #"f4924dc9ad672ee8c4f8c84743301af5"}
        zomato = actions.zomatopy.initialize_app(config)
        loc = tracker.get_slot('location')
        cuisine = tracker.get_slot('cuisine')
        budget = tracker.get_slot('budget')
        emailID = tracker.get_slot('emailID')
        
        print('Email ID - ' + emailID)
        location_detail=zomato.get_location(loc, 1)
        d1 = json.loads(location_detail)
        lat=d1["location_suggestions"][0]["latitude"]
        lon=d1["location_suggestions"][0]["longitude"]
  
        cuisines_dict={'chinese':25,'mexican':73,'italian':55,'american':1,'north indian':50,'south indian':85}
        restaurant_found_count = 0        # to call the API multiples times, until 5 best restaurants in budget are not found
        search_offset = 0                # to search for next 20 restaurants in the zomato result list (max 20 rest. are received in search API)
        response=""
        rest_df = pd.DataFrame(columns=['Name', 'Location', 'Avg. Rating', 'Avg. Cost of 2 people'])

        # keep experiencing time-out error due to multiple API calls        
        # while(restaurant_found_count < 10 and search_offset < 100):
        results=zomato.restaurant_search_by_rating("", lat, lon, str(cuisines_dict.get(cuisine)), search_offset)
        json_result = json.loads(results)
        rest_name_list = []
        rest_location_list = []
        rest_rating_list = []
        rest_price_list = []
        if json_result['results_found'] == 0:
            dispatcher.utter_message("No Results")
        else:
            rest_name_list = [restaurant['restaurant']['name'] for restaurant in json_result['restaurants']]
            rest_location_list = [restaurant['restaurant']['location']['address'] for restaurant in json_result['restaurants']]
            rest_rating_list = [restaurant['restaurant']['user_rating']['aggregate_rating'] for restaurant in json_result['restaurants']]
            rest_budg_list = [restaurant['restaurant']['average_cost_for_two'] for restaurant in json_result['restaurants']]
            pd.set_option('display.max_colwidth', None)
            df = pd.DataFrame({'Name':rest_name_list, 'Location':rest_location_list, 'Avg. Rating':rest_rating_list, 'Avg. Cost of 2 people':rest_budg_list})
            if budget == "low":
            	df = df[df['Avg. Cost of 2 people']<300]
            elif budget == "mid":
            	df = df[(df['Avg. Cost of 2 people']>=300) & (df['Avg. Cost of 2 people']<=700)]
            else:
            	df = df[(df['Avg. Cost of 2 people']>700)]
          
        restaurant_found_count = restaurant_found_count + len(df.index)
        #search_offset = search_offset+20 	   
        rest_df = pd.concat([rest_df, df])
             	
        rest_df_html = rest_df.head(10).to_html(index=False)
        html_msg = "<p>Hey there!<br>Here are the top %s restaurants around %s for %s budget : <br><br>"%(cuisine,loc,budget)+rest_df_html+"</p>"
        send_mail.mail_results(emailID, html_msg)
        return []
        


class ActionSlotReset(Action):  
    def name(self):         
        return 'action_slot_reset' 
    def run(self, dispatcher, tracker, domain):         
        return[AllSlotsReset()]	