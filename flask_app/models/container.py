from flask_app.config.mysqlconnection import connectToMySQL
import datetime
from flask import flash, session, request

class Container:
    DB = "containerproject_schema"
    def __init__( self , data ):
        self.id = data['id']
        self.height = data['height']
        self.width = data['width']
        self.length = data['length']
        self.forsale = data['forsale']
        self.saleprice = data['saleprice']
        self.forrent = data['forrent']
        self.rentprice = data['rentprice']
        self.containerimg = data['containerimg']
        self.description = data['description']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.customers_id = data['customers_id']

    @classmethod
    def save(cls, data ):
        query = """
            INSERT INTO containers ( height, width, length, forsale, saleprice, forrent, rentprice, containerimg, description, created_at, updated_at, customers_id ) 
            VALUES ( %(height)s, %(width)s, %(length)s, %(forsale)s, %(saleprice)s, %(forrent)s, %(rentprice)s, %(containerimg)s, %(description)s, now(), now(), %(customers_id)s  );
            """
        result = connectToMySQL(cls.DB).query_db( query, data )
        return result
    
    @classmethod
    def edit(cls, data):
        query = """
            UPDATE containers SET height=%(height)s, width=%(width)s, length=%(length)s, forsale=%(forsale)s, saleprice=%(saleprice)s, forrent=%(forrent)s, rentprice=%(rentprice)s, containerimg=%(containerimg)s, description=%(description)s, updated_at=now(), customers_id=%(customers_id)s 
            WHERE containers.id = %(id)s;
        """
        result = connectToMySQL(cls.DB).query_db( query, data )
        return result

    @classmethod
    def get_all_containers(cls):
        query = "SELECT * from containers"
        results = connectToMySQL(cls.DB).query_db(query)
        containerslist = []
        for single_container in results:
            this_container = cls(single_container)
            containerslist.append(this_container)
        return containerslist
    
    @classmethod
    def get_one_container(cls, id):
        query = "SELECT * FROM containers WHERE id = %(id)s;"
        results = connectToMySQL(cls.DB).query_db(query, {'id': id})
        for container in results:
            this_container = cls(container)
        return this_container
    
    @classmethod
    def delete(cls, id):
        query = """DELETE FROM containers
            WHERE id = %(id)s;"""
        return connectToMySQL(cls.DB).query_db(query,{"id": id})

    @staticmethod
    def validate_container(container):
        is_valid = True 
        if int(container['height']) < 1:
            flash("Height must be at least 1 foot.", 'container')
            is_valid = False
        if int(container['width']) < 1:
            flash("Width must be at least 1 foot.", 'container')
            is_valid = False
        if int(container['length']) < 1:
            flash("Length must be at least 1 foot.", 'container')
            is_valid = False
        if container['forsale'] ==  1 and len(container['saleprice']) < 1:
            flash("If the container is for sale, a sale price must be provided.", 'container')
            is_valid = False
        if container['forrent'] == 1 and len(container['rentprice']) < 1:
            flash("If the container is for rent, a rent price must be provided.", 'container')
            is_valid = False
        if len(container['description']) < 1:
            flash("Description must be provided.", 'container')
            is_valid = False
        return is_valid