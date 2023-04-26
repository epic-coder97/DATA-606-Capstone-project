#https://dev.to/chukhraiartur/scrape-google-flights-with-python-4dln
from playwright.sync_api import sync_playwright
from selectolax.lexbor import LexborHTMLParser
import json, time
import pandas as pd



def get_page(playwright, from_place, to_place, departure_date, return_date):
    page = playwright.chromium.launch(headless=False).new_page()
    page.goto('https://www.google.com/travel/flights?hl=en-US&curr=USD')

    # type "From"
    from_place_field = page.query_selector_all('.e5F5td')[0]
    from_place_field.click()
    time.sleep(1)
    from_place_field.type(from_place)
    time.sleep(1)
    page.keyboard.press('Enter')

    # type "To"
    to_place_field = page.query_selector_all('.e5F5td')[1]
    to_place_field.click()
    time.sleep(1)
    to_place_field.type(to_place)
    time.sleep(1)
    page.keyboard.press('Enter')

    # type "Departure date"
    departure_date_field = page.query_selector_all('[jscontroller="s0nXec"] [aria-label="Departure"]')[0]
    departure_date_field.click()
    time.sleep(1)
    departure_date_field.type(departure_date)
    time.sleep(1)
    page.query_selector('.WXaAwc .VfPpkd-LgbsSe').click()
    time.sleep(1)

    # type "Return date"
    return_date_field = page.query_selector_all('[jscontroller="s0nXec"] [aria-label="Return"]')[0]
    return_date_field.click()
    time.sleep(1)
    return_date_field.type(return_date)
    time.sleep(1)
    page.query_selector('.WXaAwc .VfPpkd-LgbsSe').click()
    time.sleep(1)

    # press "Explore"
    page.query_selector('.MXvFbd .VfPpkd-LgbsSe').click()
    time.sleep(2)

    # press "More flights"
    page.query_selector('.zISZ5c button').click()
    time.sleep(2)

    parser = LexborHTMLParser(page.content())
    page_url = page.url
    page.close()

    return parser, page_url


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
        print(type(data))
        print(page_url)


    return data

def create_df(data):
    # Access the "best_departing_flights" and "other_departing_flights" keys in the dictionary
    best_departing_flights_data = data["best_departing_flights"]
    other_departing_flights_data = data["other_departing_flights"]

    # Create dataframes from the extracted data
    best_departing_flights_df = pd.DataFrame(best_departing_flights_data)
    other_departing_flights_df = pd.DataFrame(other_departing_flights_data)

    # Display the dataframes
    # print("Best Departing Flights Dataframe:")
    # print(best_departing_flights_df)
    # print("\nOther Departing Flights Dataframe:")
    # print(other_departing_flights_df)

    return best_departing_flights_df , other_departing_flights_df


def run(playwright):
    from_place = 'BWI'
    to_place = 'Las Vegas'
    departure_date = '5-1-2023'
    return_date = '5-4-2023'

    parser, page_url = get_page(playwright, from_place, to_place, departure_date, return_date)
    google_flights_results = scrape_google_flights(parser, page_url)

    #print(json.dumps(google_flights_results, indent=2, ensure_ascii=False))
    df1, df2 = create_df(google_flights_results)
    print(df1)
    print('\n')
    print(df2)
    return  df1 , df2

    #df1.to_csv('df1.csv' , index=False)
    #df2.to_csv('df2.csv', index=False)



with sync_playwright() as playwright:
    run(playwright)