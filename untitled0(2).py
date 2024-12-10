# -*- coding: utf-8 -*-
"""Untitled0.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1T7PYNgDbf2dvaLAShWslySfUHgpMM_mb
"""

# Commented out IPython magic to ensure Python compatibility.
# %%writefile app.py

!pip install tensorflow pandas numpy scikit-learn streamlit

!pip install py-localtunnel

!pip install pyngrok

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

data_books = pd.read_csv('/content/drive/MyDrive/BookRecSys/dataset/Books.csv')
data_books.fillna(0, inplace=True)
data_users = pd.read_csv('/content/drive/MyDrive/BookRecSys/dataset/Users.csv')
data_users.fillna(0, inplace=True)
data_ratings = pd.read_csv('/content/drive/MyDrive/BookRecSys/dataset/Ratings.csv')
data_ratings.fillna(0, inplace=True)

# # Merge books and ratings data on 'isbn'
merged_data = pd.merge(data_books, data_ratings, on='ISBN')

# # Create a pivot table with book titles and average ratings
# pivot_table = merged_data.pivot_table(index='Book-Title', values='Book-Rating', aggfunc='mean')
# localtunnel@2.0.2
# # Generate the heatmap
# plt.figure(figsize=(10, 8))
# sns.heatmap(pivot_table, annot=True, cmap='coolwarm', linewidths=.5)
# plt.title('Average Ratings of Books')
# plt.xticks(rotation=90)  # Rotate x-axis labels if needed
# plt.show()

import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

user_encoder = LabelEncoder()
isbn_encoder = LabelEncoder()

merged_data['User-ID'] = user_encoder.fit_transform(merged_data['User-ID'])
merged_data['ISBN'] = isbn_encoder.fit_transform(merged_data['ISBN'])

# Prepare the data for training
X = merged_data[['User-ID', 'ISBN']]
y = merged_data['Book-Rating']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Build the model
model = tf.keras.Sequential([
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(1)
])

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model
model.fit(X_train, y_train, epochs=5, validation_data=(X_test, y_test))

print("Model training complete.")

import streamlit as st

# Define a function to get recommendations for a given user ID
def get_recommendations(user_id):
    # Encode the user ID
    encoded_user_id = user_encoder.transform([user_id])[0]

    # Create a DataFrame with all possible ISBNs for the given user ID
    all_isbns = merged_data['ISBN'].unique()
    user_isbns = pd.DataFrame({'User-ID': [encoded_user_id] * len(all_isbns), 'ISBN': all_isbns})

    # Predict ratings for all books for the given user ID
    predicted_ratings = model.predict(user_isbns)

    # Add predicted ratings to the DataFrame
    user_isbns['predicted_rating'] = predicted_ratings

    # Merge with book titles
    recommendations = pd.merge(user_isbns, data_books[['ISBN', 'Book-Title']], on='ISBN')

    # Sort by predicted rating in descending order and return top 10 recommendations
    top_recommendations = recommendations.sort_values(by='predicted_rating', ascending=False).head(10)

    return top_recommendations[['Book-Title', 'predicted_rating']]

# Streamlit front end
st.title('Book Recommendation System')
user_id_input = st.number_input('Enter User ID', min_value=0, step=1)
if st.button('Get Recommendations'):
    recommendations = get_recommendations(user_id_input)
    st.write(recommendations)

# import logging
# import streamlit as st

# logging.basicConfig(level=logging.DEBUG)

# st.title('Book Recommendation System')
# user_id_input = st.number_input('Enter User ID', min_value=0, step=1)
# if st.button('Get Recommendations'):
#     try:
#         recommendations = get_recommendations(user_id_input)
#         st.write(recommendations)
#     except Exception as e:
#         logging.error(f"Error getting recommendations: {e}")
#         st.error(f"Error getting recommendations: {e}")

# from pyngrok import ngrok

# # Set your ngrok authtoken
# ngrok.set_auth_token("")

# !ngrok http 8501 --log=stdout &

# # Start the Streamlit app
# !streamlit run app.py

# import requests

# # Get the public URL from ngrok API
# response = requests.get('http://localhost:4040/api/tunnels')
# public_url = response.json()['tunnels'][0]['public_url']
# print(f"Streamlit app is live at {public_url}")

# !streamlit run app.py & npx localtunnel --port 8501 --subdomain bookrecsys

# !curl https://loca.lt/mytunnelpassword