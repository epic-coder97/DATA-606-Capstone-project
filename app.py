from flask import Flask, render_template, request
# import openai_secret_manager
import openai
import os
import json

from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
from selectolax.lexbor import LexborHTMLParser
import json, time
import pandas as pd
import googlemaps
import requests
import re
from recommendations import *
app = Flask(__name__)
import concurrent.futures

# Load OpenAI API credentials
# secrets = openai_secret_manager.get_secret("openai")
api_key = 'API-key'
openai.api_key = api_key


@app.route("/")
def about():
    return render_template("about.html")


@app.route("/index")
def index():
    return render_template("Home.html")

@app.route("/itinerary", methods=["POST"])
def generate_itinerary():

    start_dest = request.form["start"]
    final_dest = request.form["end"]
    num_days = request.form["days"]
    budget = request.form["budget"]

    # Get the city name from the user.
    start_city = start_dest
    dest_city = final_dest
    pattern = r"(.*Airport)"
    api_key = "google_API"
    # Use the Google Maps Places API to get the place ID for the location.
    gmaps = googlemaps.Client(key=api_key)

    #   For START
    result = gmaps.places(query=start_city, type='airport')

    # Get the details for the first result.
    details = gmaps.place(place_id=result['results'][0]['place_id'], fields=['name', 'geometry', 'address_component'])

    # Extract the IATA code from the address components.
    iata_code_start = details['result']['name']
    match = re.search(pattern, iata_code_start)

    if match:
        iata_code_start = match.group(1)
        print(iata_code_start)
    else:
        print("No match found.")

    # Print the IATA code.
    print("The airport for " + start_city + " is " + iata_code_start)

    # for DEST

    result = gmaps.places(query=dest_city, type='airport')

    # Get the details for the first result.
    details = gmaps.place(place_id=result['results'][0]['place_id'], fields=['name', 'geometry', 'address_component'])

    # Extract the IATA code from the address components.
    iata_code_dest = details['result']['name']
    match = re.search(pattern, iata_code_dest)

    if match:
        iata_code_dest = match.group(1)
        print(iata_code_dest)
    else:
        print("No match found.")
    # Print the IATA code.
    print("The airport for " + dest_city + " is " + iata_code_dest)
    user_input = (iata_code_start, iata_code_dest, num_days, budget)

    model_engine = "text-davinci-003"
    # prompt = f"Generate a detailed {num_days}-day itinerary from {start_dest} to {final_dest} and also places to visit in {final_dest}."
    # prompt = f"Can you help me plan an itinerary for my upcoming trip? I'm starting in {start_dest} and I want to explore {final_dest}, and I have {num_days} to spend. Can you suggest a detailed itinerary for me?"
    prompt = f"Act as an professional travel agent.Generate an itinerary for a trip starting at {start_dest} and exploring {final_dest}. The itinerary should include {num_days} " \
             f"days and cover the following details: recommended activities, places to eat, accommodation " \
             f"options ( suggest only one accommodation based on the budget {budget} for the entire trip ) , transportation options ( from the start destination to final Desination), and any other relevant information to ensure a memorable trip. " \
             f"Give the total estimate for the whole trip as well as for each day. " \
             f"Suggest only 1 accommodation for the whole trip which fits the budget {budget} at the start of the itinerary."
    # f"Also, Display the output in JSON format."
    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    print(type(response))
    itinerary = response.choices[0].text.strip()
    itinerary = itinerary.replace("\n", "<br>")
    print(type(itinerary))
    text_file = open("itinerary.txt", "w")
    n = text_file.write(itinerary)
    text_file.close()

    with open('itinerary.txt', 'r') as file:
        text = file.read()
    with sync_playwright() as playwright:
        run(playwright, user_input)

    return render_template("itinerary.html", itinerary=text , user_input= user_input)

@app.route("/trip_itinerary")
def trip_itinerary():
    with open('itinerary.txt', 'r') as file:
        text = file.read()
    return render_template("trip.html", itinerary=text)


def print_inputs(user_input):
    print(type(user_input))
    (start_dest, final_dest, num_days, budget) = user_input


def get_page_flights(page, from_place, to_place, departure_date, return_date):
    # type "From"
    from_place_field = page.query_selector_all('.e5F5td')[0]
    from_place_field.click()
    time.sleep(1)
    from_place_field.type(from_place)
    time.sleep(1)
    page.keyboard.press('Enter')
    page.keyboard.press('Tab')

    # type "To"
    to_place_field = page.query_selector_all('.e5F5td')[1]
    to_place_field.click()
    time.sleep(1)
    to_place_field.type(to_place)
    time.sleep(1)
    page.keyboard.press('Enter')
    page.keyboard.press('Tab')

    # type "Departure date"
    departure_date_field = page.query_selector_all('[jscontroller="s0nXec"] [aria-label="Departure"]')[0]
    time.sleep(1)
    departure_date_field.fill(departure_date)
    time.sleep(1)
    page.keyboard.press('Tab')
    time.sleep(2)

    # type "Return date"
    return_date_field = page.query_selector_all('[jscontroller="s0nXec"] [aria-label="Return"]')[0]
    time.sleep(1)
    return_date_field.fill(return_date)
    time.sleep(1)
    page.query_selector('.WXaAwc .VfPpkd-LgbsSe').click()
    time.sleep(1)

    # press "Explore"
    page.query_selector('.MXvFbd .VfPpkd-LgbsSe').click()
    time.sleep(2)

    # press "More flights"
    page.query_selector('.zISZ5c button').click()
    time.sleep(2)
    time.sleep(2)
    time.sleep(2)

    parser = LexborHTMLParser(page.content())
    page_url = page.url

    return parser, page_url


def get_page_hotels(page):
    time.sleep(2)
    page.click('#\\38  > div.VfPpkd-RLmnJb')
    time.sleep(2)
    time.sleep(2)
    time.sleep(2)

    # code to take all the data
    # text = page.query_selector('.PyIgrd').text_content()
    # print(text)
    # number = int(text.split()[-1])
    # print(number)
    # n = int(number / 20)  # division will round down automatically
    # just taking data from first 5 pages
    n = 5
    df = pd.DataFrame()
    for i in range(n):
        parser = LexborHTMLParser(page.content())
        page_url = page.url
        # next button
        page.query_selector('.eGUU7b button').click()
        time.sleep(2)
        time.sleep(2)
        time.sleep(2)
        google_hotels_result = scrape_google_hotels(parser, page_url)
        df = pd.concat([df, google_hotels_result], ignore_index=True)

    time.sleep(2)
    page.close()

    return df


def scrape_google_flights(parser, page_url):
    data = {}

    categories = parser.root.css('.zBTtmb')
    category_results = parser.root.css('.Rk10dc')

    for category, category_result in zip(categories, category_results):
        category_data = []

        for result in category_result.css('.yR1fYc'):
            date = result.css('[jscontroller="cNtv4b"] span')
            departure_date = date[0].text()
            arrival_date = date[1].text()
            company = result.css_first('.Ir0Voe .sSHqwe').text()
            duration = result.css_first('.AdWm1c.gvkrdb').text()
            stops = result.css_first('.EfT7Ae .ogfYpf').text()
            emissions = result.css_first('.V1iAHe .AdWm1c').text()
            emission_comparison = result.css_first('.N6PNV').text()
            price = result.css_first('.U3gSDe .FpEdX span').text()
            price_type = result.css_first('.U3gSDe .N872Rd').text() if result.css_first('.U3gSDe .N872Rd') else None

            flight_data = {
                'departure_date': departure_date,
                'arrival_date': arrival_date,
                'company': company,
                'duration': duration,
                'stops': stops,
                'emissions': emissions,
                'emission_comparison': emission_comparison,
                'price': price,
                'price_type': price_type,
                'flight_link': page_url
            }

            airports = result.css_first('.Ak5kof .sSHqwe')
            service = result.css_first('.hRBhge')

            if service:
                flight_data['service'] = service.text()
            else:
                flight_data['departure_airport'] = airports.css_first('span:nth-child(1) .eoY5cb').text()
                flight_data['arrival_airport'] = airports.css_first('span:nth-child(2) .eoY5cb').text()

            category_data.append(flight_data)

        data[category.text().lower().replace(' ', '_')] = category_data
        print(page_url)

    return data


def scrape_google_hotels(parser, page_url):
    data = []

    for result in parser.root.css('.uaTTDe'):
        result_dict = {}

        if result.css_first('.hVE5 .ogfYpf'):
            result_dict['ad'] = result.css_first('.hVE5 .ogfYpf').text().replace('  ', ' ')

        result_dict['title'] = result.css_first('.QT7m7 h2').text()
        result_dict['link'] = 'https://www.google.com' + result.css_first('.PVOOXe').attributes.get('href')
        price = result.css_first('.OxGZuc .kixHKb span')
        result_dict['price'] = price.text() if price else None
        rating = result.css_first('.FW82K .KFi5wf')
        result_dict['rating'] = float(rating.text()) if rating else None
        reviews = result.css_first('.FW82K .jdzyld')
        result_dict['reviews'] = int(reviews.text()[2:-1].replace(',', '')) if reviews else None
        result_dict['extensions'] = [extension.css_first('.sSHqwe').text() for extension in
                                     result.css('.RJM8Kc .HlxIlc div, li')]
        result_dict['thumbnails'] = [
            thumbnail.attributes.get('src') if thumbnail.attributes.get('src') else thumbnail.attributes.get(
                'data-src')
            for thumbnail in result.css('.NBZP0e .q5P4L')
        ]

        data.append(result_dict)
        print(page_url)
        df = pd.DataFrame(data)
    return df


def create_df_flights(data):
    # Access the "best_departing_flights" and "other_departing_flights" keys in the dictionary
    best_departing_flights_data = data["best_departing_flights"]
    other_departing_flights_data = data["other_departing_flights"]

    # Create dataframes from the extracted data
    best_departing_flights_df = pd.DataFrame(best_departing_flights_data)
    other_departing_flights_df =pd.DataFrame(other_departing_flights_data)

    return best_departing_flights_df, other_departing_flights_df

@app.route('/reccomendation')
def recomendation():
   a = our_recommendation()
   flight_recomendations = pd.read_csv('flight_recommendations.csv')
   hotel_recommendations = pd.read_csv('hotel_recommendations.csv')
   cards = []
   for i, row in flight_recomendations.iterrows():
       card = f"""
           <div class="card">
               <div class="card-body">
                   <h5 class="card-title">{row['departure_airport']} - {row['arrival_airport']}</h5>
                   <p class="card-text">Departure time: {row['departure_time']}</p>
                   <p class="card-text">Arrival time: {row['arrival_time']}</p>
                   <p class="card-text">Duration: {row['duration']}</p>
                   <p class="card-text">Stops: {row['stops']}</p>
                   <p class="card-text">Airline: {row['company']}</p>
                   <p class="card-text">Price: {row['price']}</p>
                   <a href="{row['flight_link']}" class="btn btn-primary">Book now</a>
               </div>
           </div>
           """
       cards.append(card)

   return render_template("reccomendation.html", cards=cards)

@app.route('/reccomendation_hotel')
def recomendation_hotels():
   a = our_recommendation()
   hotel_recommendations = pd.read_csv('hotel_recommendations.csv')
   cards = []
   for i, row in hotel_recommendations.iterrows():
       card = f"""
           <div class="card">
               <div class="card-body">
                   <h5 class="card-title">{row['title']}</h5>
                   <p class="card-text">Ratings: {row['rating']}</p>
                   <p class="card-text">Amenities: {row['extensions']}</p>
                   <p class="card-text">Price: ${row['price']} per night</p>
                   <a href="{row['link']}" class="btn btn-primary">Book now</a>
               </div>
           </div>
           """
       cards.append(card)

   return render_template("hotels_reco.html", cards=cards )


def run(playwright, user_input):
    page = playwright.chromium.launch(headless=False).new_page()
    page.goto('https://www.google.com/travel/flights?hl=en-US&curr=USD')
    (start_dest, final_dest, num_days, budget) = user_input
    from_place = start_dest
    to_place = final_dest
    departure_date = '5/19/2023'
    return_date = '5/30/2023'

    flight_parser, flight_page_url = get_page_flights(page, from_place, to_place, departure_date, return_date)
    google_flights_results = scrape_google_flights(flight_parser, flight_page_url)
    df = get_page_hotels(page)
    df.to_csv('df.csv', index=False)

    df1, df2 = create_df_flights(google_flights_results)
    df1.to_csv('df1.csv', index=False)
    df2.to_csv('df2.csv', index=False)
    recomendation()

    # return render_template("reccomendation.html", df1=df1, df2=df2)


# with sync_playwright() as playwright:
#     run(playwright)

if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 8080)))
