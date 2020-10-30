import os
import sqlite3
from sqlite3 import Error
from flask import Flask, request, render_template
from flask import request, redirect
from twilio.twiml.messaging_response import MessagingResponse
import random

app = Flask(__name__)

def respond(message):
    response = MessagingResponse()
    response.message(message)
    return str(response)

@app.route('/webhook', methods=['POST'])
def reply():
    sender_phone_number = request.form.get('From')
    media_msg = request.form.get('NumMedia')   
    instagram_response = request.form.get('Body')   
    message_latitude = request.values.get('Latitude')
    message_longitude = request.values.get('Longitude')

    # check if the user already sent in a pic. if they send something new, then update it
    try:
        conn = sqlite3.connect('/Users/diane/Documents/projects/giveawayform/app.db')
        cur = conn.cursor()
        query = """SELECT EXISTS (SELECT 1 FROM users WHERE phone_number = (?))"""
        cur.execute(query, [sender_phone_number])      
        query_result = cur.fetchone()
        user_exists = query_result[0]

        if user_exists == 0: 
            # print("[INFO] : instagramusername that needs to be inserted = ", instagram_response)
            insert_users = '''INSERT INTO users(phone_number)
                        VALUES(?)'''
            cur = conn.cursor()
            cur.execute(insert_users, (sender_phone_number,))
            conn.commit()
            query = """SELECT id FROM users WHERE phone_number = (?)"""
            cur.execute(query, [sender_phone_number])      
            query_result = cur.fetchone()
            # print("[DATA] : query_result = ", query_result)
            user_id = query_result[0]
            # print("[DATA] : user_id = ", user_id)           
            insert_socialmedia = ''' INSERT INTO socialmedia (user_id, instagram)
                        VALUES(?, ?) '''
            cur = conn.cursor()
            cur.execute(insert_socialmedia, (user_id, instagram_response,))
            # print("[DATA] : inserted ig name ", instagram_response, " for userid ", user_id)
            conn.commit()
            return respond(f'Thanks for joining the giveaway! If your username changed, please respond with your new username.')            
        
        if user_exists == 1:
            look_up_user_query = """SELECT id FROM users WHERE phone_number = (?)"""
            cur.execute(look_up_user_query, [sender_phone_number]) 
            query_result = cur.fetchone()
            user_id = query_result[0]
            # print("[DATA] : setting the IG name of ", instagram_response, " to user_id = ", user_id)
            update_user_picture = '''UPDATE socialmedia
                    SET instagram = ?
                    WHERE user_id = ?'''
            cur = conn.cursor()
            cur.execute(update_user_picture, (instagram_response, user_id))
            conn.commit()
            return respond(f'You already joined the giveaway and updated your entry with the username {instagram_response}.')            
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
    return respond(f'Uh oh how did we get here?')
    

@app.route('/winner')
def enter_giveaway():
    number = 0
    try:
        conn = sqlite3.connect('/Users/diane/Documents/projects/giveawayform/app.db')
        cur = conn.cursor()
        query = """SELECT COUNT (phone_number) FROM users;"""
        cur.execute(query)      
        total_entries = cur.fetchone()
        total_entries = total_entries[0]
        print("\n[DATA] : total_entries = ", total_entries)

        # generate the random winner
        generated_number = random.randrange(1, total_entries+1)
        
        cur = conn.cursor()
        look_up_winner_query = """SELECT users.id, phone_number, instagram FROM users JOIN socialmedia ON (socialmedia.id = users.id) WHERE user_id = (?);"""
        cur.execute(look_up_winner_query, [generated_number]) 
        winner_entry = cur.fetchone()
        print("[DATA] = winner = ", winner_entry)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
    return render_template('success.html', variable=winner_entry)

# @app.route("/")
@app.route('/', methods=['GET', 'POST'])
def viewentries():
    try:
        conn = sqlite3.connect('/Users/diane/Documents/projects/giveawayform/app.db')
        cur = conn.cursor()
        query = """SELECT users.id, phone_number, instagram FROM users JOIN socialmedia	ON (socialmedia.id = users.id);"""
        cur.execute(query)      
        query_result = cur.fetchall()
        print("\n[DATA] : queryresult = ", query_result)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
    return render_template('index.html', variable=query_result)

