from flask_app.config.mysqlconnection import connectToMySQL
import datetime
from flask import flash, session
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class Customer:
    DB = "containerproject_schema"
    def __init__( self , data ):
        self.id = data['id']
        self.firstname = data['firstname']
        self.lastname = data['lastname']
        self.email = data['email']
        self.password = data['password']
        self.isadmin = data['isadmin']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.favorites = []

    @classmethod
    def save(cls, data ):
        query = """
                INSERT INTO customers ( firstname , lastname , email, password, isadmin, created_at, updated_at ) 
                VALUES ( %(firstname)s , %(lastname)s , %(email)s, %(password)s, False, now(), now() );
                """
        result = connectToMySQL(cls.DB).query_db( query, data )
        return result

    @classmethod
    def update(cls, data ):
        query = """
                UPDATE customers SET password=%(password)s, updated_at=now()
                WHERE customers.id = %(id)s;
                """
        result = connectToMySQL(cls.DB).query_db( query, data )
        return result

    @classmethod
    def already_exists(cls, customer):
        exists = False
        query = """SELECT * from customers WHERE email = %(email)s;"""
        check = connectToMySQL(cls.DB).query_db(query,customer)
        if check:
            exists = True
        return exists
    
    @classmethod
    def get_customer_by_email(cls,data):
        query = "SELECT * FROM customers WHERE email = %(email)s;"
        result = connectToMySQL(cls.DB).query_db(query,data)
        if len(result) < 1:
            return False
        return cls(result[0])

    @classmethod
    def get_customer_by_id(cls,data):
        query = "SELECT * FROM customers WHERE id = %(id)s;"
        result = connectToMySQL(cls.DB).query_db(query,data)
        if len(result) < 1:
            return False
        return cls(result[0])
    
    @classmethod
    def get_all_customers(cls):
        query = "SELECT * from customers"
        results = connectToMySQL(cls.DB).query_db(query)
        customerslist = []
        for single_customer in results:
            this_customer = cls(single_customer)
            customerslist.append(this_customer)
        return customerslist

    @staticmethod
    def validate_registration(customer):
        is_valid = True 
        if len(customer['firstname']) < 3:
            flash("First name is required and must be more than 2 characters.", 'register')
            is_valid = False
        if len(customer['lastname']) < 3:
            flash("Last name is required and must be more than 2 characters.", 'register')
            is_valid = False
        if len(customer['email']) < 1:
            flash("Email is required.", 'register')
            is_valid = False
        if not EMAIL_REGEX.match(customer['email']): 
            flash("Invalid email address!", 'register')
            is_valid = False
        exists = Customer.already_exists(customer)
        if exists:
            flash("An account for this email address already exists.", 'register')
            is_valid = False
        number_count = 0
        cap_letter_count = 0
        for letter in customer['password']:
            if letter.isdigit():
                number_count += 1
            if letter.isupper():
                cap_letter_count += 1
        if number_count < 1 or cap_letter_count < 1 or len(customer['password']) < 8:
            flash("Password must be more than 8 characters, and contain at least one number and at least one capital letter.", 'register')
            is_valid = False
        if customer['password'] != customer['confirm_pw']:
            flash("Passwords do not match.", 'register')
            is_valid = False
        return is_valid
    
    @staticmethod
    def validate_passwordchange(customer):
        is_valid = True 
        number_count = 0
        cap_letter_count = 0
        for letter in customer['newpassword']:
            if letter.isdigit():
                number_count += 1
            if letter.isupper():
                cap_letter_count += 1
        if number_count < 1 or cap_letter_count < 1 or len(customer['newpassword']) < 8:
            flash("Password must be more than 8 characters, and contain at least one number and at least one capital letter.", 'password_change')
            is_valid = False
        if customer['newpassword'] != customer['confirm_pw']:
            flash("New passwords do not match.", 'password_change')
            is_valid = False
        return is_valid