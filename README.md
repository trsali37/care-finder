# 🩹 CareFinder
## 📹 [Video Demo](https://youtu.be/hPzeuXvL3tc)

## 💡 Inspiration

During my tenure as an analyst at UnitedHealth Group, I encountered a 2019 organizational [study](https://www.unitedhealthgroup.com/newsroom/posts/2019-07-22-high-cost-emergency-department-visits.html) showing that treating common conditions in Emergency Rooms costs over 900% more than in Urgent Cares. This compounds up to 18 Million Avoidable Hospital Emergency Department Visits, and $32 Billion in Costs to the Health Care System Each Year!

Often times individuals instinctively rush to hospital emergency rooms for any medical need. However, studies show that two thirds of these hospital visits could be treated at Urgent Cares. This common behavior stems from lack of information needed to make informed decisions about where to seek appropriate treatment. By choosing the right care facility, patients can potentially save significant time avoiding long waits in crowded emergency rooms and reduce their costs by up to 10 times.

I recognized that this disparity had immense potential for improving healthcare accessibility and reducing costs. At the time I had limited technical skills which prevented me from developing actionable solutions to address this problem.

Now that I've taken CS50P, I want to take the opportunity to develop a python program that has been in the back of my mind since then.

## 🌠 Description:
My goal is to create a program that empowers users to:

1. Identify appropriate care setting (Emergency Rooms or Urgent Cares) for medical needs
2. Locate nearby healthcare providers quickly and easily
3. Help users make informed decisions that can potentially save both time and money

This project aims to guide users towards more cost effective and efficient healthcare choices, ultimately contributing to better healthcare utilization and improved patient experiences.


## 🔬 Scope
### 🗽**Geographic Coverage:**    New York, NY addresses ONLY
- May expand scope to other areas in the future, but limited to New York, NY for minimal viable product
### 🙋 **Target Users:**          Individuals seeking immediate, non life threatening medical care
### **Value Proposition:**
- 💰 Potential cost savings:      By directing users to appropriate care locations, this can reduce patient expenses by up to 10x
- 🧭 Care Navigation:             Provide sufficient information to guide users to the nearest care location to help them make informed decisions
- 🏥 Emergency Room Decongestion: Improve health care efficiency and wait times at hospitals

## Features
### ⚡ Instantly determine whether your symptoms require Urgent Care or Emergency attention
- Symptoms classification is based on medical resources below:
    - 🏥 [the Mayo Clinic Health System](https://www.mayoclinichealthsystem.org/hometown-health/speaking-of-health/emergency-vs-urgent-care-whats-the-difference)
    - 🏥 [Sarasota Memorial Health Care System](https://www.smh.com/blog/urgent-care-or-er-a-guide-by-symptom)
### 📍 Locate the closest healthcare provider near your location
- 🌟 Powered by the comprehensive [National Provider Identifier database](https://npiregistry.cms.hhs.gov/search)
- ⏱️ Ensures real time accuracy of up to date provider information
### 🚗 Provide distance and duration to health care provider
  - 🌐 Utilizes [geopy](https://geopy.readthedocs.io/en/stable/), a renowned and reliable Python geocoding library
  - 🚦 Integrates [Mapbox API](https://docs.mapbox.com/api/navigation/matrix/) for advanced distance and duration calculations

## Terminal Guide
1. Run $ project.py in Terminal
2. Enter symptoms, multiple symptoms must be comma separated
    - **Example:** `cough, fever, seizures`
3. Provide Address, full address recommended for accuracy
    - **Example:** `234 W 42nd St, New York, NY 10036`
4. Confirm the standardized address (yes/no)
5. Recommendation will return:
    - Nearest care organization name
    - Distance and Duration travel time
    - Address of care location
    - **Example:**
        - `The nearest Urgent Care to 234 West 42nd Street, New York, NY, 10036 is MEDRITE MEDICAL CARE, located 0.19 miles away.`
        - `It is approximately a 2 min drive.`
        - `The address is 330 W 42ND ST, NEW YORK, NY, 10036`

## Concepts and Technologies
- API requests (GET and POST requests, access token, rate limit)
- Conditional Arguments
- Regular Expression
- For and While Loops
- List and Dictionary Comprehensions
- Geopy Library
- Exception Handling
- Unit Test
- Dictionary, List, Pandas Dataframe
- String Functions

## Requirements
```python
import requests
import json
import pandas as pd
import re
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import inflect
import sys
```

## API List
### NPI Registry
*The NPI Registry API retrieves data from NPPES daily. The National Plan and Provider Enumeration System (NPPES) is a database that assigns unique identifiers to health care providers and health plans.*
- **Usage:**  To find health care providers based on search criteria
- **Input:**  GET Request filtered by taxomonomy code (Urgent Care or Emergency Medicine) and address
- **Output:** JSON Response of health care providers
- **Limitations**:
    - An API query will return a maximum of 200 results per request.
    - Maximum of 1,200 records over six requests.
- **Documentation:**: [NPI Registry API Documentation](https://npiregistry.cms.hhs.gov/api-page)

### Mapbox API
*The Mapbox Matrix API returns travel times between many points*
- **Usage:**  To find the distance and duration between user input address and the care locations
- **Input:**  GET Request with latitude and longitude coordinates of source and destinations
- **Output:** JSON Response of the duration in seconds and the distance in meters (straight line distance, not driving distance) on the fastest route for each element in the matrix
- **Limitations**:
    - For the mapbox/driving
        - Maximum 25 input coordinates per request.
        - Maximum 60 requests per minute.
- **Documentation:**: [Mapbox Documentation](https://docs.mapbox.com/api/navigation/matrix/)

### Geopy
*Python Library that makes it easy to locate the coordinates of addresses, cities, countries, and landmarks across the globe using third-party *
- **Usage:**  Geocoding and address standardization
- **Input:**  String Address
- **Output:** Float latitude and longitude
- **Considerations:**
    - Nominatim Geocoder
        - Requires user_agent parameter for Nominatim geocoder
        - Geopy may raise too many requests error. Adding timeout duration to Geopy Nomination will give geopy more time for responses. This will allow for continued attempts to get results behind the scenes rather than continuously returning multiple errors that are visible in the terminal.
    - Use rate limiter to handle multiple geocoding requests efficiently
    - Set appropriate timeout to manage "too many requests" errors
    - Geopy accesses different API services notably OpenStreetMap, Google Geocoding API, US Census, etc.
- **Documentation:** [Geopy Documentation](https://geopy.readthedocs.io/en/stable/) , [Geopy Github](https://github.com/geopy/geopy)

### ZipcodeAPI
*Multi-Radius endpoint finds zip codes within a specified radius of a source zip code*
- **Usage:**  Find surrounding zip codes when no care locations found in the initial address
- **Input:**  POST request with user input address or zip code
- **Output:** JSON response of a list of zip codes
- **Consider:**
    - Requires API Key unlocked through sign up
    - Free tier usage up to 10 requests per hour
    - Max radius extends to 3000 miles
    - Geographic Coverage in US and Canada only
- **Note:** Use sparingly due to request limits
- **Documentation:** [ZipcodeAPI Documentation](https://www.zipcodeapi.com/API#multi-radius)

## Main() Steps
### 1. Prompt for Symptoms
*Prompt user for symptoms, return cleaned symptom list and formatted string for care setting recommendation*

- **Function:** `return_user_symptom, clean_user_symptom = get_user_symptom()`
- **Process:**
    1. Check if any input symptom matches ER symptoms in data dictionary
    2. If all symptoms match UC, suggest Urgent Care
    3. If symptom not found in dictionary, default to Emergency Medicine
    4. Return Output
- **Input:**  `What Symptoms Do You Have? (e.g cough,fever):` Comma separated values in terminal, case insensitive, and extra spaces ignored
    - **Valid Examples:** There must be values between commas
        - `cough`
        - `cough, fever`
        - ` cough ,  fever ,`
    - **Invalid Examples:** Empty values or comma separated with spaces
        - ` `       (empty)
        - ` ,  `    (only commas and spaces)
        - ` , , , ` (empy values comma separated)
- **Output:**
    - `clean_user_symptoms`: List of symptoms stripped of extra spaces and lowercased
        - **Example:**
            - `["cough","fever"]`
    - `return_user_symptom`: Grammatically correct string using inflect library
        - **Example:**
            - `"cough"`
            - `"cough and fever"`
            - `"cough, fever, and seizures"`
- **NOTE:** Reprompt will occur if no values input

### 2. Determine Care Setting Based on Symptoms
*Recommend Emergency Room or Urgent Care based on symptoms*
- **Process:**
    1. Run `symptom(clean_user_symptom)` function
    2. Print the care setting recommendation
    3. Returns string care setting
- **Function:** `care_type = determine_care_type(return_user_symptom, clean_user_symptom)`
- **Input:**    `return_user_symptom`, `clean_user_symptom`
- **Output:**
    - Prints the care setting recommendation in the terminal
        - **Example:** `"Based on theses symptom(s) of cough, we recommend you to go to Urgent Care."`
    - Returns string care setting
        - **Example:** `"Emergency Medicine"` or `"Urgent Care"`
- **Test:** # `#user_symptom = ["covid","chest pain","fatigue"]`


#### 2A. Assess Symptoms for Emergency Room or Urgent Care
*Based on Symptoms, determine appropriate care setting (Emergency Room or Urgent Care)*
- **Process:**
  1. Check for ER symptoms in data dictionary
  2. Suggest Urgent Care if all symptoms match UC
  3. Default to ER for unknown symptoms
  4. Return Output
- **Function:**    `symptom(user_symptom)`
- **Input:**        List of user input symptoms
- **Output:**       String `"Emergency Medicine"` or `"Urgent Care"`
- **Future State:** Expand symptoms dictionary or leverage an external source with updated symptoms
- **Documentation:** [Symptoms Guide](https://www.smh.com/blog/urgent-care-or-er-a-guide-by-symptom)

### 3. Prompt for User Address and Locate Nearest Care Location
*Standardize, validate, and geocode address*
- **Process:**
    1. Prompt for address
    2. Standardize address, reprompt if address can not be found
    3. Confirm standardized address with user, reprompt if user inputs "No"
    4. Transform to dictionary format
    5. Append geocode data, reprompt if address can not be geocoded
    6. Return Output
- **Function:**     `input_dict`, `valid_address = get_geocoded_user_address()`
- **Input:**        Function will prompt in the terminal for an address
    - **Example:**  `"234 W 42nd St, New York, NY 10036"` or `"234 W 42nd St"`
- **Output:**
    - Dictionary of user standardized address with geocode
        - **Example:** `{'Address': '234 West 42nd Street', 'City': 'New York', 'State': 'NY', 'Zip Code': '10036', 'Longitude': '-73.98843804512987', 'Latitude': '40.7562126', 'Geocoded': True}`
    - Standardized/valid address string
        - **Example:** `"234 W 42nd St, New York, NY 10036"`
- **Notes:** This step is crucial, users could put in many variations of their address but having the standardized address will help ensure its integrity
- **Future State:**
    - Instead of hard coded dictionary of symptoms, use a external source that encompasses a larger more accurate database.
    - Include logic to determine severity of sypmtoms

#### 3A. Standardize User Input Address
*Convert string address to standardized format using geopy library*

- **Process:**
1. Use geocode to return address details of input address
2. Get address values
3. Return Output
- **Function:**      `standardize(input_address)`
- **Input:**         String address, does not need to be complete.
    - **Example:**   `"234 W 42nd St, New York, NY 10036"` or `"234 W 42nd St"`
- **Output:**        Standardized address string or False if not found
    - **Example:**   `"234 W 42nd St, New York, NY 10036"`
- **Consideration:** City and state are hardcoded for current scope
- **Notes:**         This standardization ensures that a real address is returned at all times unless address is invalid
- **Test:**          # input_address = "234 W 42nd St, New York, NY 10036"
- **Future State:**  Future versions may expand geographical scope

#### 3B. Transform Address to Dictionary
- **Purpose:**     Transform standardized address string to dictionary
- **Process:**
1. Use Regex Search to parse valid address using regex
2. Returns Output
- **Function:**    `address_dict(valid_address)`
- **Input:**       Standardized address string
    - **Example:** `"234 W 42nd St, New York, NY 10036"`
- **Output:**      Address Dictionary containing of Address, City, State, Zip
    - **Example:** `{'Address': '234 West 42nd Street', 'City': 'New York', 'State': 'NY', 'Zip Code': '10036'}`
- **Notes:** City and state are hardcoded for MVP
- **Test:** # input_address = "234 W 42nd St, New York, NY 10036"
- **Future State:** - Improve Regex to parse City and State more dynamically, raw City returns "City of New York", and State returns "New York"

#### 3C. Append Coordinates to Address Dictionary
*Add latitude, longitude, and geocoding status to address data*
- **Function:**    `get_geocode(input_dict)`
- **Process:**
    1. Build an address string from the address dictionary
    2. Use rate limiter since geocode times out often
    3. Return Output
- **Input:**       Dictionary data structures with Address, City, State, Zip Code keys, designed to be iterated if input contains multiple rows
- **Output:**      Returns variables (Longitude, Latitude, True/False)
    - **Example:** `{'Longitude': '-73.98843804512987', 'Latitude': '40.7562126', 'Geocoded': True}`

### 4. Determine Care Locations Based on User Address
*Find care locations using NPI Registry API, transform response into dataframe, and append geocode*
- **Function:**   `care_df = care(care_type, input_dict["Zip Code"])`
- **Process:**
    1. Call `find_provider()` to get care locations within user's zip code
    2. If no locations found within user zip code, expand search to city/state for a wider net
        - Utilize `zipcodes()`to find nearest zip codes within a 1 mile radius
            - Subsequent calls increase the radius by 1 mile each loop
    4. Repeat cycle until matches are found
    5. Filter results:
        - Locations are actual provider locations, not mailing addresses
        - Facilities are in the correct city and state
        - Taxonomy code that primarily specializes Urgent Care or Emergency Medicine
    6. Clean and transform accurate data into a pandas dataframe
    7. Return output
- **Input:**
    - `care_type`:  Result from symptom function
    - `zip_code`:   From standardized address
- **Output:**       Pandas dataframe of all care locations
- **Limit:**
    - MapBox API limited to max 24 coordinates
    - NPI Registry API limited to one zip code per call
    - ZipcodeAPI limited to 50 calls per day / 10 calls per hour
- **Notes:**        Pandas data frame used to easily transform data
- **Future State:** Improve logic for finding additional zipcodes, care facilities outside city could be futher than 1 mile radius

#### 4A. FIND PROVIDER
*Find care locations near input address*
- **Function:**    `find_provider(care_type,zip_code)`
- **Process:**
    1. Build API NPI Registry request string with care setting and zip code
    2. GET Request
    3. Return Output
- **Input:**
    - `care_type`:  Result from symptom function
    - `zip_code`:   From standardized address
- **Output:**       JSON response of care locations
- **Limit:**
    - NPI Registry allows for unlimited calls but filter is limited to one zip code per request
    - An API query will return a maximum of 200 results per request.
    - Maximum of 1,200 records over six requests.
- **Test:**        # zip_code = "10009" #10065 for 2 locations
                   # care_type = "Emergency Room"

#### 4B. find zipcodes nearest to user input address
*Get zip codes within specified radius*
- **Function:**     `zipcode()`
- **Process:**
    1. Build POST ZipCodeAPI request string with zip code and radius
    2. POST request
    3. Take zip codes from response and form a list of nearby zipcodes
    4. Return Output
- **Input:**
    - Standardized zip code
    - Search radius increases with each `care()` call
- **Output:**        List of zip codes strings
- **Limit:**         ZipCodeAPI Free Tier
    - 50 calls per day
    - 10 calls per hour
- **Consideration:** This API was used for MVP, not the best way to get nearby zip codes for larger scale
- **Test:** Use `234 West 42nd Street, New York, NY, 10036` address to test for usage of this function, it should return a address not within input zip code

### 5. Travel Metrics
*Get distance and driving duration between user address and care locations*
- **Function:** `match = care_distance_duration(input_dict,care_df)`
- **Process:**
  1. Build Mapbox API request with all coordinates
  2. GET request
  3. Extract distance and duration from response
  4. Convert distance to miles and duration to hours/minutes
  5. Return Output
- **Input:**     Geocoded user address dictionary and care locations dataframe
- **Output:**    Updated care location dataframe with distance and duration
- **Limit:** Mapbox API Free Tier
  - 24 coordinates per call
  - 3000 calls per month
- **Consideration:**
    - Use virtual environment to hide access token
    - Mapbox API has other options alternative transportation methods such as walking, biking, and consider traffic
    - Distance is currently determined in straight line distance between address and care locations

#### 5A. Convert Seconds to Minutes/Hours
*Convert seconds to user friendly format*
- **Function:** `zipcode(zip_code,zip_code_radius)`
- **Process:**
    1. Divide seconds into hours, minutes, and remaining seconds
    2. Create string based on calculation
    3. Handle singular and plural forms
    4. Return Output
- **Input:**     Float value in seconds
- **Output:**    Formatted time string
    - **Examples:**
        - `"0 min"`       (30 seconds)
        - `"1 min"`       (31 seconds)
        - `"59 min"`      (3550 seconds)
        - `"1 hr, 0 min"` (3600 seconds)
        - `"1 hr, 23 min"`(5000 seconds)
- **Test:**      #zip_code = "10009"

### 6. Recommendation
*Provide information about nearest care location*
- **Process:**
    1. Extract information from the first row of the sorted data frame
    2. Format the recommendation string with extracted data
    3. Return Output
- **Input:**   Care data frame sorted from shortest distance
- **Output:** String together
    - Care setting (Urgent Care or Emergency Room)
    - User's address
    - Name of the nearest facility
    - Distance to the facility
    - Estimated travel time
    - Care location full address
    - **Example:**
        - `"The nearest Urgent Care to 234 West 42nd Street, New York, NY, 10036 is MEDRITE MEDICAL CARE, located 0.19 miles away.`
        - `It is approximately a 2 min drive.`
        - `The address is 330 W 42ND ST, NEW YORK, NY, 10036"`
- **Future State:** May want to allow user to ask for how many results they want to see, or may want to sort by duration


