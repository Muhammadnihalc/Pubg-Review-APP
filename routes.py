from flask import Flask, Blueprint, render_template, redirect, url_for, jsonify
import sqlite3
import threading
from initialize_db import initialize_database
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import logging


bp = Blueprint('routes', __name__)

def create_db_connection():
    logging.info('connected to db.')
    db_connection = sqlite3.connect('steam_reviews.db')
    cursor = db_connection.cursor()
    return db_connection, cursor


def fetch_latest_reviews(db_connection, cursor):
    cursor.execute("SELECT steamid, review_text, posted_time FROM reviews WHERE review_text IS NOT NULL ORDER BY posted_time DESC LIMIT 10")
    reviews = cursor.fetchall()
    return reviews

def fetch_top_sensational_reviews(db_connection, cursor):
    cursor.execute("SELECT steamid, review_text, comment_count, num_likes FROM reviews WHERE review_text IS NOT NULL ORDER BY comment_count DESC LIMIT 5")
    reviews = cursor.fetchall()
    return reviews

def update_sentiment_scores(db_connection, cursor):
    cursor.execute("SELECT steamid, review_text FROM reviews WHERE sentiment_score IS NULL")
    rows = cursor.fetchall()
    analyzer = SentimentIntensityAnalyzer()

    for row in rows:
        steamid, review_text = row[0], row[1]
        sentiment_score = analyzer.polarity_scores(review_text)["compound"]

        # Update the sentiment score in the database
        cursor.execute("UPDATE reviews SET sentiment_score = ? WHERE steamid = ? AND review_text = ?", (sentiment_score, steamid, review_text))

    db_connection.commit()

def fetch_reviews_by_sentiment(db_connection, cursor):
    sentiment_categories = ["Very Positive", "Positive", "Neutral", "Negative", "Very Negative"]
    top_reviews = {}

    for category in sentiment_categories:
        score_ranges = {
            "Very Positive": (0.5, 1.0),
            "Positive": (0.1, 0.5),
            "Neutral": (-0.1, 0.1),
            "Negative": (-0.5, -0.1),
            "Very Negative": (-1.0, -0.5)
        }

    
        min_score, max_score = score_ranges[category]


        cursor.execute("SELECT steamid, review_text, num_likes FROM reviews WHERE sentiment_score >= ? AND sentiment_score <= ? ORDER BY num_likes DESC LIMIT 1", (min_score, max_score))
        row = cursor.fetchone()

        if row:
            top_reviews[category] = row

    return top_reviews


def count_feature_reviews(db_connection, cursor):
    sentiment_categories = ["Very Positive", "Positive", "Neutral", "Negative", "Very Negative"]
    feature_counts = {category: 0 for category in sentiment_categories}
    analyzer = SentimentIntensityAnalyzer()

    
    cursor.execute("SELECT review_text FROM reviews WHERE review_text LIKE ? AND review_text IS NOT NULL", ('%feature%',))
    feature_reviews = cursor.fetchall()

    for review_text in feature_reviews:
        sentiment_score = analyzer.polarity_scores(review_text[0])["compound"]
        for category in sentiment_categories:
            min_score, max_score = get_score_range(category)
            if min_score <= sentiment_score <= max_score:
                feature_counts[category] += 1

    return feature_counts

def get_score_range(category):
    score_ranges = {
        "Very Positive": (0.5, 1.0),
        "Positive": (0.1, 0.5),
        "Neutral": (-0.1, 0.1),
        "Negative": (-0.5, -0.1),
        "Very Negative": (-1.0, -0.5)
    }
    return score_ranges[category]


def count_graphics_reviews(db_connection, cursor):
    sentiment_categories = ["Very Positive", "Positive", "Neutral", "Negative", "Very Negative"]
    graphics_counts = {category: 0 for category in sentiment_categories}
    analyzer = SentimentIntensityAnalyzer()


    cursor.execute("SELECT review_text FROM reviews WHERE review_text LIKE ? AND review_text IS NOT NULL", ('%graphics%',))
    graphics_reviews = cursor.fetchall()

    for review_text in graphics_reviews:
        sentiment_score = analyzer.polarity_scores(review_text[0])["compound"]
        for category in sentiment_categories:
            min_score, max_score = get_score_range(category)
            if min_score <= sentiment_score <= max_score:
                graphics_counts[category] += 1

    return graphics_counts


@bp.route('/')
def home():
    logging.info('Home route accessed.')
    return render_template('home.html')

    
@bp.route('/initialize')
def initialize():
    try:
        logging.info('db initialization started.')
        db_connection, cursor = create_db_connection()
        
        initialize_database(db_connection, cursor)

        return jsonify({"message": "Data collection started. Redirecting to the menu page."})
    except Exception as e:
        logging.error(f'Error during initialization: {str(e)}')
        return jsonify({"error": str(e)})


@bp.route('/menu')
def menu():
    return render_template('menu.html')


@bp.route('/view')
def view_reviews():
    try:
        db_connection, cursor = create_db_connection()
        cursor.execute("SELECT DISTINCT steamid, review_text, posted_time FROM reviews WHERE review_text IS NOT NULL ORDER BY posted_time DESC LIMIT 10")
        reviews = cursor.fetchall()

        return render_template('view.html', reviews=reviews)
    except Exception as e:
        logging.error(f'Error during displaying the records: {str(e)}')
        return jsonify({"error": str(e)})

@bp.route('/sensational')
def sensational_reviews():
    try:
        db_connection, cursor = create_db_connection()

        cursor.execute("SELECT DISTINCT steamid, review_text, comment_count, num_likes FROM reviews WHERE review_text IS NOT NULL ORDER BY comment_count DESC LIMIT 5")
        reviews = cursor.fetchall()

        return render_template('sensational.html', reviews=reviews)
    except Exception as e:
        logging.error(f'Error at sensational: {str(e)}')
        return jsonify({"error": str(e)})


@bp.route('/sentimental')
def sentimental_reviews():
    try:
        db_connection, cursor = create_db_connection()

    
        update_sentiment_scores(db_connection, cursor)
        top_reviews = fetch_reviews_by_sentiment(db_connection, cursor)
        db_connection.close()

        return render_template('sentimental.html', categorized_reviews=top_reviews)
    except Exception as e:
        logging.error(f'Error at sentimental: {str(e)}')
        return jsonify({"error": str(e)})



@bp.route('/overallCount')
def overall_count():
    try:
        db_connection, cursor = create_db_connection()
        sentiment_categories = ["Very Positive", "Positive", "Neutral", "Negative", "Very Negative"]
        sentiment_counts = {}

        score_ranges = {
            "Very Positive": (0.5, 1.0),
            "Positive": (0.1, 0.5),
            "Neutral": (-0.1, 0.1),
            "Negative": (-0.5, -0.1),
            "Very Negative": (-1.0, -0.5)
        }

        for category in sentiment_categories:
            cursor.execute("SELECT COUNT(*) FROM reviews WHERE sentiment_score >= ? AND sentiment_score <= ?", score_ranges[category])
            count = cursor.fetchone()[0]
            sentiment_counts[category] = count

        return render_template('overallCount.html', sentiment_counts=sentiment_counts)
    except Exception as e:
        logging.error(f'Error during at overall: {str(e)}')
        return jsonify({"error": str(e)})


@bp.route('/mostLiked')
def most_liked_reviews():
    try:
        db_connection, cursor = create_db_connection()

        cursor.execute("""
            SELECT r.steamid, r.review_text, r.num_likes 
            FROM reviews r
            WHERE review_text IS NOT NULL
            AND r.id = (
                SELECT id
                FROM reviews
                WHERE steamid = r.steamid
                ORDER BY num_likes DESC
                LIMIT 1
            )
            ORDER BY r.num_likes DESC 
            LIMIT 5
        """)

        top_liked_reviews = cursor.fetchall()

        db_connection.close()

        return render_template('mostLiked.html', top_liked_reviews=top_liked_reviews)
    except Exception as e:
        logging.error(f'Error during mostliked: {str(e)}')
        return jsonify({"error": str(e)})



@bp.route('/mostDisliked')
def most_disliked_reviews():
    try:
        db_connection, cursor = create_db_connection()

        cursor.execute("""
            SELECT steamid, review_text, num_dislikes 
            FROM (
                SELECT DISTINCT steamid, review_text, num_dislikes 
                FROM reviews 
                WHERE review_text IS NOT NULL 
                ORDER BY num_dislikes DESC
            ) AS subquery
            LIMIT 5
        """)

        top_disliked_reviews = cursor.fetchall()

        db_connection.close()

        return render_template('mostDisliked.html', top_disliked_reviews=top_disliked_reviews)
    except Exception as e:
        logging.error(f'Error at mostdisliked: {str(e)}')
        return jsonify({"error": str(e)})

@bp.route('/feature')
def feature_reviews():
    try:
        db_connection, cursor = create_db_connection()
        feature_counts = count_feature_reviews(db_connection, cursor)

        db_connection.close()

        return render_template('feature.html', feature_counts=feature_counts)
    except Exception as e:
        return jsonify({"error": str(e)})

@bp.route('/graphics')
def graphics_reviews():
    try:
        db_connection, cursor = create_db_connection()
        graphics_counts = count_graphics_reviews(db_connection, cursor)

        db_connection.close()

        return render_template('graphics.html', graphics_counts=graphics_counts)
    except Exception as e:
        logging.error(f'Error at grapics: {str(e)}')
        return jsonify({"error": str(e)})

