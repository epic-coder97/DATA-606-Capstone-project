import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def preprocess_flightdata(flight_df1, flight_df2):
    flight_df = pd.concat([flight_df1, flight_df2])
    # print(flight_df.head(1))

    # split duration into hours and minutes columns
    flight_df[["hours", "minutes"]] = flight_df["duration"].str.split(" ", expand=True)[[0, 2]]

    # convert to numeric using to_numeric()
    flight_df["hours"] = pd.to_numeric(flight_df["hours"])
    flight_df["minutes"] = pd.to_numeric(flight_df["minutes"])
    flight_df['duration_in_mins'] = (flight_df['hours'] * 60) + (flight_df['minutes'])

    # replace NaN values with 0 in the dataframe
    flight_df.fillna(0, inplace=True)

    # remove the currency sign from the price column and convert to numeric type
    flight_df['price'] = pd.to_numeric(flight_df['price'].str.replace(r'[^0-9.]', '', regex=True))

    # Remove unwanted columns
    flight_df.drop(['emissions', 'emission_comparison', 'hours', 'minutes'], axis=1, inplace=True)

    # rename columns using a dictionary
    flight_df = flight_df.rename(columns={"departure_date": "departure_time", "arrival_date": "arrival_time"})

    # filter out rows with price == 0.0
    flight_df = flight_df[flight_df['price'] != 0.0]

    return flight_df


def preprocess_hoteldata(hotel_df):
    hotel_df.drop(['ad', 'thumbnails'], axis=1, inplace=True)

    # remove the currency sign from the price column and convert to numeric type
    hotel_df['price'] = pd.to_numeric(hotel_df['price'].str.replace(r'[^0-9.]', '', regex=True))

    # drop rows where "hotelname" column is empty
    hotel_df = hotel_df[hotel_df["title"].notna()]

    # replace NaN values with 0 in the dataframe
    hotel_df.fillna(0, inplace=True)

    # filter out rows with price == 0.0
    hotel_df = hotel_df[hotel_df['price'] != 0.0]

    return hotel_df


# define a function to get the top n most similar flights to a given flight
def get_top_similar_recommendations(id, df, n=10):
    # create a TF-IDF vectorizer object to convert the features column into a matrix of feature vectors
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['features'])

    # compute the cosine similarity matrix between all flights
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    sim_scores = list(enumerate(cosine_sim[id]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    top_similar_recommendations = [i[0] for i in sim_scores[1:n + 1]]
    return top_similar_recommendations


# define a function to recommend the cheapest flights based on a given flight
def cheapest_recommendations(id, df, attributes):
    top_similar_recommendations = get_top_similar_recommendations(id, df)
    sorted_similar_recommendations = df.iloc[top_similar_recommendations].sort_values(by=attributes, ascending=True)
    return sorted_similar_recommendations.head(10)


def recommendation_engine(df, features, attributes):
    df['features'] = df[features].apply(lambda x: ' '.join(x), axis=1)

    recommendations = cheapest_recommendations(5, df, attributes)
    return recommendations


def our_recommendation():
# if __name__ == '__main__':
    # Load the data into a pandas dataframe
    flight_data1 = pd.read_csv('df1.csv')
    flight_data2 = pd.read_csv('df2.csv')
    hotels_data = pd.read_csv('df.csv')

    # Define features for the recommendation engine
    flight_features = ['stops', 'company']
    hotel_features = ['extensions']
    flight_engine_attributes = ['price', 'duration_in_mins']
    hotel_engine_attributes = ['price', 'rating']

    flight_data = preprocess_flightdata(flight_data1, flight_data2)
    hotel_data = preprocess_hoteldata(hotels_data)

    flight_recommendations = recommendation_engine(flight_data, flight_features, flight_engine_attributes)
    flight_recommendations.head(5).to_csv('flight_recommendations.csv', index=False)

    hotel_recommendations = recommendation_engine(hotel_data, hotel_features, hotel_engine_attributes)
    hotel_recommendations.head(5).to_csv('hotel_recommendations.csv', index=False)
