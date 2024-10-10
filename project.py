import requests
import json #used for testing
import pandas as pd
import re
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import inflect
import sys
inf = inflect.engine()

#SCOPE = NEW YORK, NY ONLY
#geopy can throw too many requests error, adding timeout duration will give geopy more time to respond, it will typically keep trying until results but instead of trying too fast and returning lots of errors for user to see
geolocator = Nominatim(user_agent="teresa", timeout = 10) #used in address_standard function, and get_geocode function

def main():
    #THERE ARE 6 STEPS OF MAIN()

    #1 - PROMPT USER FOR SYMPTOMS, clean symptoms and apply to a list, and apply inflect
    return_user_symptom, clean_user_symptom = get_user_symptom()

    #2 - CHECK IF THE SYMPTOMS CAN BE CARED FOR AT URGENT CARE OR EMERGENCY ROOM
    care_type = determine_care_type(return_user_symptom, clean_user_symptom)

    #3 - PROMPT USER FOR LOCATION, while loop reprompts user at any point address is being processed to input a valid address
    input_dict, valid_address = get_geocoded_user_address()

    #4 - #CREATE PANDAS DF OF ALL CARE LOCATIONS, and apply geocode
    care_df = care(care_type, input_dict["Zip Code"])

    #5 - FIND THE DISTANCE AND DURATION BETWEEN THE USER ADDRESS AND THE CARE LOCATIONS
    match = care_distance_duration(input_dict,care_df)
    # print(match) #FOR TESTING PURPOSES

    #6 - RECOMMENDING TO USER THE FIRST AND CLOSEST CARE LOCATION BY DISTANCE
    #keeping a df of the other choices in case i want to prompt user for another option, and go down the list of all care locations
    print(
    f"The nearest {care_type} to {valid_address} is {match["Organization Name"].iloc[0]}, located {match["Distance"].iloc[0]} away.\n"
    f"It is approximately a {match["Duration"].iloc[0]} drive.\n"
    f"The address is {match["Address"].iloc[0]}, {match["City"].iloc[0]}, {match["State"].iloc[0]}, {match["Zip Code"].iloc[0]}"
    )

def get_user_symptom():
    clean_user_symptom = []
    while not clean_user_symptom:

        user_symptoms = input("What Symptoms Do You Have? (e.g cough,fever): ").lower().strip()
        if not user_symptoms:
            print("At least one symptom must be entered, please enter symptom(s)")
            continue
        clean_user_symptom = [symptom.strip() for symptom in user_symptoms.split(",") if symptom.strip()]
        if not clean_user_symptom:
            print("Input can not be empty, please enter a valid symptom(s)")

    return_user_symptom = inf.join(clean_user_symptom)

    return return_user_symptom, clean_user_symptom

def determine_care_type(return_user_symptom, clean_user_symptom):
    care_type = symptom(clean_user_symptom)
    if care_type:
        print(f"Based on theses symptom(s) of {return_user_symptom}, we recommend you to go to {care_type}.")
    return care_type

def symptom(clean_user_symptom):
    data = {
        "covid":"UC",
        "fatigue":"UC",
        "cough":"UC",
        "sore throat":"UC",
        "body ache":"UC",
        "seizures":"ER",
        "broken bones":"ER",
        "loss of vision":"ER",
        "fainting":"ER",
        "chest pain":"ER",
        "allergies":"UC",
        "animal bites":"UC",
        "insect bites":"UC",
        "tick removal":"UC",
        "bone fractures":"UC",
        "bronchitis":"UC",
        "congestion, nasal and chest":"UC",
        "colds":"UC",
        "diarrhea":"UC",
        "ear infection":"UC",
        "fever":"UC",
        "flu":"UC",
        "un-wellness":"UC",
        "minor asthma":"UC",
        "minor burns":"UC",
        "minor cuts":"UC",
        "pink eye":"UC",
        "rashes":"UC",
        "sinus infection":"UC",
        "sports injuries":"UC",
        "sprain":"UC",
        "strain":"UC",
        "stings":"UC",
        "sunburn or sun poisoning":"UC",
        "upper respiratory infection":"UC",
        "urinary tract infections":"UC",
        "flu":"UC",
        "pneumonia":"UC",
        "tetanus":"UC",
        "pertussis":"UC",
        "shingles":"UC",
        "vomiting":"UC"
    }
    #iterate over each symptom in user_syptom list
    for symptom in clean_user_symptom:
        if symptom not in data:
            return "Emergency Room"
        elif data[symptom] == "ER":
            return "Emergency Room"
    return "Urgent Care"

def get_geocoded_user_address():
    check_address = True

    while check_address:
        input_address = input(f"What is your location so that we can find you the closest care site? ").strip()
        #STANDARDIZE ADDRESS, user MAY put incomplete address located in NEW YORK, NY, a standardized address will be returned
        valid_address = standardize_address(input_address)

        if not valid_address:
            print("Invalid Address. Please Enter a Valid Address.")
            continue

        confirm = input(f"Please confirm your address is {valid_address}. (yes/no): ").lower().strip()
        if confirm == "no":
            continue

        input_dict = address_dict(valid_address)
        if not input_dict:
            print("Unable to parse email. Please Enter a Valid Address.")
            continue

        care_geocode = get_geocode(input_dict)
        if not care_geocode:
            print("Address unable to be geocoded. Please Enter a Valid Address.")
            continue

        input_dict["Longitude"], input_dict["Latitude"], input_dict["Geocoded"] = get_geocode(input_dict) #apply tuple to dict
        check_address = False
    return input_dict, valid_address

def standardize_address(input_address):

    try:
        address = geolocator.geocode(input_address, addressdetails = True, exactly_one = True) #WILL RETURN NONE IF ADDRESS CAN NOT BE FOUND
        if address:
            address = address.raw
            house_number = address["address"].get("house_number", "")
            road = address["address"].get("road", "")
            # state = address["address"].get("state", "NY") #the state gets returned fully written out NEW YORK
            # city = address["address"].get("city", "New York") #city gets returned as CITY OF NEW YORK
            state = "NY"
            city = "New York"
            zip_code = address["address"].get("postcode", "")
            full_address = f"{house_number} {road}, {city}, {state}, {zip_code}".strip() #added strip in case house number is blank, all else should be filled
            # print(full_address) #FOR TESTING PURPOSES
            return full_address
        else:
            return False
    except Exception as e:
        print(f"An error occurred while geocoding: {e}")
        return False

def address_dict(valid_address):

    if matches := re.search(r"^(.+)\s?,\s?(.+),\s?(..),?\s?(\d{5})", valid_address): #will return None if re.search doesnt find match
        input_data = {
            'Address': matches.group(1),
            'City': matches.group(2),
            'State': matches.group(3),
            'Zip Code': matches.group(4)
        }
        return input_data
    else:
        return False

def get_geocode(addy):

    #addy = [{'Care Setting': 'Emergency Medicine', 'Organization Name': 'RESOLUT MEDICAL GROUP PA', 'Address': '85 5TH AVE', 'City': 'NEW YORK', 'State': 'NY', 'ZIP Code': '100033019', 'Telephone Number': '212-993-7809', 'Last Updated': '2024-06-12'}]
    address = f"{addy['Address']}, {addy['City']}, {addy['State']} {addy['Zip Code'][:5]}"
    # print(address)
    geocoder = RateLimiter(geolocator.geocode, min_delay_seconds=3) #RATE LIMITER USED SINCE GEOCODE TIMES OUT
    location = geocoder(address)
    if location:
        return str(location.longitude), str(location.latitude), True #return 3 variables
    else:
        return None, None, False
    # print((d_location.longitude,d_location.latitude)) #-73.9824559,40.7383463, -73.982196, 40.7513547

def care(care_setting, zip_code):

    if care_setting == "Emergency Room": #for user literacy
        care_setting = "Emergency Medicine" #for api taxonomy accuracy

    matches = False
    first_call = True #if false then flow has already been processed through
    call = 0
    data = []
    nearby_zip_codes = []
    zip_code_radius = 1
    location_address = []

    while not matches:

        if first_call:
            response = find_provider(care_setting,zip_code)
            first_call = False
            call += 1
            # view = json.dumps(response.json(), indent = 2) #FOR TESTING PURPOSES
            # print(view) #FOR TESTING PURPOSES
        else:
            #IF THERE ARE NO CARE LOCATIONS IN ZIP THEN RETURN CARE LOCATIONS WITHIN CITY,STATE
            response = find_provider(care_setting,"")
            nearby_zip_codes = zipcode(zip_code,zip_code_radius)
            call += 1
            zip_code_radius += 1
            # view = json.dumps(response.json(), indent=2) #FOR TESTING PURPOSES
            # print(f"Second Call : {view}") #FOR TESTING PURPOSES

        if response["result_count"] > 0:
            matches = True
        else:
            continue

        for result in response["results"]:
            organization_name = result["basic"]["organization_name"] #organizaiton name
            last_updated = result["basic"]["last_updated"] #when data was last updated in npi registry

            for address in result["addresses"]: #since there could be mailing or location addresses, filter for the data from the location address
                if address["address_purpose"] == "LOCATION" and address["city"] == "NEW YORK":
                    if call > 1:
                        if address["postal_code"][:5] in nearby_zip_codes:
                            location_address = address
                            break
                    else:
                        location_address = address
                        break
            if not location_address:
                continue
            # print(location_address) #FOR TESTING PURPOSES

            for taxonomy in result["taxonomies"]:#ensure the primary specialty of the organization is either UC or ER
                if care_setting in taxonomy["desc"] and taxonomy["primary"]:
                    data.append({
                        "Care Setting": care_setting,
                        "Organization Name": organization_name,
                        "Address": location_address["address_1"],
                        "City": location_address["city"],
                        "State": location_address["state"],
                        "Zip Code": location_address["postal_code"][:5],
                        "Telephone Number": location_address.get("telephone_number", None),
                        "Last Updated": last_updated
                    })
                else:
                    break

        matches = False if not data else True
        if matches:
            break
        elif not matches and call > 1:
                raise ValueError("Could not find match")
    care_df = pd.DataFrame(data)
    # print(df) #FOR TESTING PURPOSES

    care_df = care_df.sort_values (by = "Last Updated", ascending = False)
    care_df = care_df.drop_duplicates(subset=["Address","Telephone Number"])
    #GEOCODE IS APPLIED TO ALL LOCATIONS
    # apply geocode function to every row, axis = 1 means to apply data as columns, result type = expand means to expand the df to include these columns
    care_df[["Longitude", "Latitude", "Geocoded"]] = care_df.apply(get_geocode, axis = 1 , result_type = "expand")
    care_df = care_df[care_df["Geocoded"] == True] #FILTER OUT CARE LOCATIONS THAT CAN NOT BE GEOCODED (not using address validation b/c cannot confirm if it is correct or not)
    care_df = care_df.head(20) #limit to 20 results because matchbox api can only handle 24 locations at a time
    care_df = care_df.reset_index(drop=True) #reindex
    # print(input_dict) #FOR TESTING PURPOSES
    # print(care_df) #FOR TESTING PURPOSES
    return care_df

def find_provider(care_type,zip_code):

    field_url = "&name_purpose=&first_name=&use_first_name_alias=&last_name=&organization_name=&address_purpose=LOCATION&city=New York&state=NY&postal_code="
    end_url = "&country_code=&limit=100&skip=&pretty=&version=2.1"
    base_url = "https://npiregistry.cms.hhs.gov/api/?number=&enumeration_type=NPI-2&taxonomy_description="
    request_string = f"{base_url}{care_type}{field_url}{zip_code}{end_url}"
    # print(request_string) #FOR TESTING PURPOSES
    try:
        response = requests.get(request_string)
    # view = json.dumps(response.json(), indent = 2) #FOR TESTING PURPOSES
    # print(view) #FOR TESTING PURPOSES
        addresses = response.json()
        # view = json.dumps(response.json(), indent=2) #FOR TESTING PURPOSES
        # print(view) #FOR TESTING PURPOSES
        return addresses
    except Exception as e:
        sys.exit(f"NPI Registry request failed: {e}")

def care_distance_duration(input_dict, care_df):
    concat_input = f"{input_dict["Longitude"]},{input_dict["Latitude"]}"
    concat_care = ';'.join(care_df["Longitude"] + "," + care_df["Latitude"])
    base_url = "https://api.mapbox.com/directions-matrix/v1/mapbox/driving/"
    field_url = "?sources=0&annotations=distance,duration&access_token="
    access_token = "" # Insert your own access token here
    request_string = f"{base_url}{concat_input};{concat_care}{field_url}{access_token}"
    # print(request_string)

    try:
        response = requests.get(request_string)
        data = response.json() #load json data into dicitonary

        # test_data = json.dumps(response.json(), indent=2) #turns json into a string for readability #FOR TESTING PURPOSES
        # print(test_data) #FOR TESTING PURPOSES
        # print(data) #FOR TESTING PURPOSES
        distances = data["distances"][0][1:] #since the data is in the inner list we must access [0], then skip the first instance since it is the source [1:].
        durations = data["durations"][0][1:]

        care_df["Distance"] = [f"{round(distance * 0.000621371, 2)} miles" for distance in distances]
        care_df["Duration"] = [duration_conversion(duration) for duration in durations]
        care_df = care_df.sort_values(by = "Distance") #must sort after conversion since the conversions
        # print(care_df)
        return care_df
    except Exception as e:
        sys.exit(f"MapBox API request failed: {e}")

def duration_conversion(seconds):

    minutes = int(round(seconds / 60, 0))
    hours = minutes // 60
    remaining_minutes = minutes % 60

    if hours > 1:
        return (f"{hours} hrs, {remaining_minutes} min")
    elif hours > 0:
        return (f"{hours} hr, {remaining_minutes} min")
    else:
        return (f"{minutes} min")

def zipcode(zip_code,zip_code_radius):

    api_key = "" # Insert your own API key here
    base_url = "https://www.zipcodeapi.com/rest/"
    end_point = "/multi-radius.json/"
    radius = str(zip_code_radius)
    unit = "/mile"
    post_data = {
        "zip_codes":zip_code
    }
    post_string = f"{base_url}{api_key}{end_point}{radius}{unit}"
    # print(post_string)
    try:
        response = requests.post(post_string,data=post_data)
        # print(f"Status Code: {response.status_code}")
        # response = requests.post("https://www.zipcodeapi.com/rest/0Fs6QHwvaNkfB9tA26e2kP3foTQ6802x38To5xi1hYni6SPT4qTdyiK5SdjQyyXY/multi-radius.json/1/mile",data=post_data) #FOR TESTING PURPOSES
        # print(f"Status Code: {response.status_code}")
        data = response.json()
        for responses in data["responses"]:
            nearby_zip_codes = responses["zip_codes"]
        # nearby_zip_codes = ['10072', '10098', '10119', '10001', '10199', '10168', '10174', '10165', '10170', '10173', '10169', '10110', '10167', '10177', '10172', '10018', '10171', '10154', '10020', '10152', '10111', '10112', '10036', '10149', '10103', '10153', '10019', '10082']
    # print(nearby_zip_codes)
        return nearby_zip_codes
    except Exception as e:
        sys.exit(f"MapBox API request failed: {e}")


if __name__ == "__main__":
    main()
