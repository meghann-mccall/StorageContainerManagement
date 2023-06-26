from flask_app.config.mysqlconnection import connectToMySQL
import datetime
from flask import flash, session
import re
 

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class User:
    DB = "beltexam_schema"
    def __init__( self , data ):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.sightings = []

    @classmethod
    def save(cls, data ):
        query = """
                INSERT INTO users ( first_name , last_name , email, password, created_at, updated_at ) 
                VALUES ( %(first_name)s , %(last_name)s , %(email)s, %(password)s, now(), now() );
                """
        result = connectToMySQL(cls.DB).query_db( query, data )
        return result

    @classmethod
    def already_exists(cls, user):
        exists = False
        query = """SELECT * from users WHERE email = %(email)s"""
        check = connectToMySQL(cls.DB).query_db(query,user)
        if check:
            exists = True
        return exists
    
    @classmethod
    def get_user_by_email(cls,data):
        query = "SELECT * FROM users WHERE email = %(email)s;"
        result = connectToMySQL(cls.DB).query_db(query,data)
        if len(result) < 1:
            return False
        return cls(result[0])

    @staticmethod
    def validate_registration(user):
        is_valid = True 
        if len(user['first_name']) < 3:
            flash("First name is required and must be more than 2 characters.", 'register')
            is_valid = False
        if len(user['last_name']) < 3:
            flash("Last name is required and must be more than 2 characters.", 'register')
            is_valid = False
        if len(user['email']) < 1:
            flash("Email is required.", 'register')
            is_valid = False
        if not EMAIL_REGEX.match(user['email']): 
            flash("Invalid email address!", 'register')
            is_valid = False
        exists = User.already_exists(user)
        if exists:
            flash("An account for this email address already exists.", 'register')
            is_valid = False
        number_count = 0
        cap_letter_count = 0
        for letter in user['password']:
            if letter.isdigit():
                number_count += 1
            if letter.isupper():
                cap_letter_count += 1
        if number_count < 1 or cap_letter_count < 1 or len(user['password']) < 8:
            flash("Password must be more than 8 characters, and contain at least one number and at least one capital letter.", 'register')
            is_valid = False
        if user['password'] != user['confirm_pw']:
            flash("Passwords do not match.", 'register')
            is_valid = False
        return is_valid