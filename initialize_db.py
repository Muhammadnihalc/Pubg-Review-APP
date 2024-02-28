import sqlite3
import requests
import datetime
import random
import time
import logging


def initialize_database(db_connection, cursor):
    logging.info('entered into initialialize_database().')
    cursor.execute('''CREATE TABLE IF NOT EXISTS reviews
                  (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                   steamid TEXT, 
                   review_text TEXT, 
                   posted_time DATETIME, 
                   sentiment_score REAL,
                   num_likes INTEGER, 
                   num_dislikes INTEGER, 
                   comment_count INTEGER)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS review_collection_status
                      (last_collection_time DATETIME)''')

   
    cursor.execute("SELECT last_collection_time FROM review_collection_status")
    last_collection_time = cursor.fetchone()

    if last_collection_time:
        last_collection_time = datetime.datetime.fromisoformat(last_collection_time[0])
        current_time = datetime.datetime.now()
        time_difference = current_time - last_collection_time

        
        if time_difference >= datetime.timedelta(hours=24):
           
            start_time = last_collection_time
            end_time = current_time

           
            fetch_and_store_reviews_within_time_range(db_connection, cursor, start_time, end_time)

           
            cursor.execute("UPDATE review_collection_status SET last_collection_time = ?", (current_time,))
            logging.info('last collection time updated .')
            db_connection.commit()  
    else:
        # If last_collection_time doesn't exist, fetch all reviews for the first time
        current_time = datetime.datetime.now()
        cursor.execute("INSERT INTO review_collection_status (last_collection_time) VALUES (?)", (current_time,))
        db_connection.commit()  
        fetch_and_store_all_reviews(db_connection, cursor)

   
    db_connection.close()

def fetch_and_store_all_reviews(db_connection, cursor):
    logging.info('entered in fetch and store all reviews().')
    
    app_id = 578080
    num_per_page = 100  # Number of reviews to fetch per page (adjust as needed)
    start_offset = 0

    # Fetch the total number of reviews to determine how many requests are needed
    total_reviews = 0
    while True:
        url = f"https://store.steampowered.com/appreviews/{app_id}?json=1&num_per_page=1&start_offset={total_reviews}"

       
        response = requests.get(url)

       
        if response.status_code == 200:
            data = response.json()

           
            if "total_reviews" in data["query_summary"]:
                total_reviews = data["query_summary"]["total_reviews"]
                break
            else:
                print("No total_reviews found in the API response.")
                break
        else:
            print(f"Failed to retrieve total_reviews. Status code: {response.status_code}")
            time.sleep(5) 

    start_time = time.time()  
    reviews_fetched = 0

    # Fetch and store reviews for up to 30 seconds
    logging.info('Fetch and store reviews for up to 1 minutes.')
    while start_offset < total_reviews and time.time() - start_time < 30:
        logging.info('fetching all review .')

        url = f"https://store.steampowered.com/appreviews/{app_id}?json=1&num_per_page={num_per_page}&start_offset={start_offset}"

        
        response = requests.get(url)

        
        if response.status_code == 200:
            
            data = response.json()

            if "reviews" in data:
                reviews = data["reviews"]

                
                for review in reviews:
                    steamid = review["author"]["steamid"]
                    review_text = review["review"]
                    posted_time = datetime.datetime.fromtimestamp(review["timestamp_created"])
                    sentiment_score = None  
                    num_likes = review["votes_up"]
                    num_dislikes = review["votes_funny"]
                    comment_count = review["comment_count"]

                    cursor.execute("INSERT INTO reviews (steamid, review_text, posted_time, sentiment_score, num_likes, num_dislikes, comment_count) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                    (steamid, review_text, posted_time, sentiment_score, num_likes, num_dislikes, comment_count))

                    reviews_fetched += 1

                db_connection.commit()
                start_offset += num_per_page
            else:
                print("No reviews found in the API response.")
                break
        else:
            print(f"Failed to retrieve reviews. Status code: {response.status_code}")
            time.sleep(5)  

    print(f"Fetched and stored {reviews_fetched} reviews in 30 seconds.")



def fetch_and_store_reviews_within_time_range(db_connection, cursor, start_time, end_time):
    logging.info('Entered into fetch_and_store_reviews_within_time_range().')
    
    app_id = 578080
    num_per_page = 100  
    start_offset = 0

    
    end_timestamp = start_time.timestamp() + 30 

    # Fetch and store reviews in batches within the specified time range
    while time.time() < end_timestamp:
        logging.info('Fetching new review.')
        url = f"https://store.steampowered.com/appreviews/{app_id}?json=1&num_per_page={num_per_page}&start_offset={start_offset}"

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()

            if "reviews" in data:
                reviews = data["reviews"]

                for review in reviews:
                    posted_time = datetime.datetime.fromtimestamp(review["timestamp_created"])

                    if start_time <= posted_time <= end_time:
                        steamid = review["author"]["steamid"]
                        review_text = review["review"]
                        sentiment_score = None  
                        num_likes = review["votes_up"]
                        num_dislikes = review["votes_funny"]
                        comment_count = review["comment_count"]

                        cursor.execute("INSERT INTO reviews (steamid, review_text, posted_time, sentiment_score, num_likes, num_dislikes, comment_count) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                        (steamid, review_text, posted_time, sentiment_score, num_likes, num_dislikes, comment_count))

                db_connection.commit()
                start_offset += num_per_page

                time.sleep(2)
            else:
                print("No reviews found in the API response.")
                break
        else:
            print(f"Failed to retrieve reviews. Status code: {response.status_code}")
            break
