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
def enter_giveaway():
    sender_phone_number = request.form.get('From')
    instagram_response = request.form.get('Body')   

    try:
        conn = sqlite3.connect('app.db')
        print("Successful connection!")

        cur = conn.cursor()
        query = """SELECT EXISTS (SELECT 1 FROM users WHERE phone_number = (?))"""
        cur.execute(query, [sender_phone_number])      
        query_result = cur.fetchone()
        user_exists = query_result[0]

        if user_exists == 0: 
            insert_users = '''INSERT INTO users(phone_number)
                        VALUES(?)'''
            cur = conn.cursor()
            cur.execute(insert_users, (sender_phone_number,))
            conn.commit()
            recent_userid = cur.lastrowid
            insert_socialmedia = ''' INSERT INTO socialmedia (user_id, instagram)
                        VALUES(?, ?) '''
            cur = conn.cursor()
            cur.execute(insert_socialmedia, (recent_userid, instagram_response,))
            conn.commit()
            return respond(f'Thanks for joining the giveaway! If your username changed, please respond with your new username.')            
        
        if user_exists == 1:
            look_up_user_query = """SELECT id FROM users WHERE phone_number = (?)"""
            cur.execute(look_up_user_query, [sender_phone_number]) 
            query_result = cur.fetchone()
            user_id = query_result[0]
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
def generate_winner():
    number = 0
    try:
        conn = sqlite3.connect('app.db')
        cur = conn.cursor()
        query = """SELECT COUNT (phone_number) FROM users;"""
        cur.execute(query)      
        total_entries = cur.fetchone()
        total_entries = total_entries[0]
        generated_number = random.randrange(0, total_entries)
        # generated_number = 5
        cur = conn.cursor()
        # more robust way because databases don't always generate ids as a sequence of numbers
        look_up_winner_query = """SELECT users.id, phone_number, instagram FROM users JOIN socialmedia ON (socialmedia.id = users.id) ORDER BY users.id LIMIT 1 OFFSET (?);"""        
        cur.execute(look_up_winner_query, [generated_number]) 
        winner_entry = cur.fetchone()
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
    return render_template('success.html', variable=winner_entry)

@app.route("/")
def viewentries():
    try:
        conn = sqlite3.connect('app.db')
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

