The Pubg review game Documentation


The application aims to  gather, store, and analyse user reviews for the PUBG  game using the Steam Game Reviews Analysis project, a web application created with Flask and SQLite. In order to examine and analyse these evaluations, this project offers a number of features, such as sentiment analysis, the top reviews by sentiment, review counts by sentiment category, and more.



1. Home Page: A landing page with general project information.

2. Initialization: An API endpoint (`/initialize`) that triggers the initialization process. It fetches user reviews for the specified game from the Steam API and stores them in the database. Typically, this route is accessed programmatically and not meant for end-users.

3. Main Menu: A menu page that provides links to various sections of the application.

4. View Latest Reviews: A page (`/view`) that displays the ten most recent user reviews for the game, fetched from the database.

5. Top Sensational Reviews: A page (`/sensational`) that displays the top five user reviews based on the number of comments and likes, fetched from the database.

6. Sentiment Analysis: A page (`/sentimental`) that performs sentiment analysis on user reviews and categorizes them into sentiment categories (e.g., Very Positive, Negative). It also displays the top-rated review for each sentiment category based on sentiment scores.

7. Overall Review Counts: A page (`/overallCount`) that calculates and displays the total counts of reviews in different sentiment categories. It provides an overview of how many reviews fall into each category (e.g., Very Positive, Neutral).

8. Most Liked Reviews: A page (`/mostLiked`) that displays the top five user reviews with the highest number of likes, fetched from the database.

9. Most Disliked Reviews: A page (`/mostDisliked`) that displays the top five user reviews with the highest number of dislikes, fetched from the database.

10. Feature and Graphics Reviews: Pages (`/feature` and `/graphics`) that count and display the number of reviews containing keywords related to features and graphics. They categorize these reviews by sentiment and provide counts for each sentiment category.

Project Structure

The project is organized into several modules:

1. app.py: The main Flask application script 

2. routes.py : the code responsible for handling HTTP requests and rendering HTML templates.

2. initialize_db.py: A script that initializes the SQLite database, creates the necessary tables, and fetches user reviews for the pubg game from the Steam API. It also handles periodic data collection to keep the database up to date.

3. Templates: Several HTML templates stored in a "templates" directory define the structure and layout of the web pages presented to the user.

4. Database : steam_review.db an sqlite databse to store data




Database Structure

The project uses an SQLite database named `steam_reviews.db` with two main tables:

1. **reviews**: This table stores user reviews along with relevant information such as the Steam ID, review text, posted time, sentiment score, number of likes, number of dislikes, and comment count.

2. **review_collection_status**: This table tracks the last collection time to ensure that data collection from the Steam API is updated at regular intervals.


Data Collection and Initialization

The `initialize_db.py` script handles the initialization of the database.
It fetches user reviews for the specified game from the Steam API and stores them in the `reviews` table.
Data collection occurs either when the database is empty or when the last collection time is more than 24 hours ago.

Sentiment Analysis

Sentiment analysis is performed using the VADER sentiment analysis library.
Reviews are categorized into sentiment categories, including Very Positive, Positive, Neutral, Negative, and Very Negative, based on their sentiment scores.


Getting Started

To get started with this project locally, follow these steps:

Install the required Python packages using `pip`:

   
   pip install -r requirements.txt
 

Start the Flask application:

   
   python app.py
  

Access the application in your web browser at `http://localhost:5000`.

