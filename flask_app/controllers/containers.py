import os
from flask_app import app
import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template, session
from flask_app.models.container import Container
from flask_app.models.customer import Customer
from werkzeug.utils import secure_filename
from os.path import join, dirname, realpath

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/inventory')
def inventory():
    all_inventory = Container.get_all_containers()
    if 'customer_id' not in session:
        return render_template("guestinventory.html", all_inventory=all_inventory)
    if 'customer_is_admin' in session:
        all_customers = Customer.get_all_customers()
        return render_template("admindash.html", all_inventory=all_inventory, all_customers = all_customers)
    return render_template("inventory.html", all_inventory=all_inventory)

@app.route('/add')
def add_container_page():   
    if 'customer_is_admin' not in session:
        return redirect('/inventory')
    all_customers = Customer.get_all_customers()
    return render_template("new.html", all_customers = all_customers)

@app.route('/container/create', methods=['POST'])
def create():
    if 'customer_is_admin' not in session:
        return redirect('/inventory')
    if not Container.validate_container(request.form):
        return redirect('/add/container')
    if 'containerimg' not in request.files:
        flash("No file part", 'container')
        return redirect('add/container')
    pic = request.files['containerimg']
    if pic.filename == '':
        flash("No image selected for uploading", 'container')
        return redirect('/add/container')
    if pic and allowed_file(pic.filename):
        filename = secure_filename(pic.filename)
        basedir = os.path.dirname(os.path.dirname(__file__))
        print('this is the basedir value: ' + basedir)
        pic.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename))
        data = {
        "height": request.form['height'],
        "width": request.form['width'],
        "length": request.form['length'],
        "forsale": request.form['forsale'],
        "saleprice": request.form['saleprice'],
        "forrent": request.form['forrent'],
        "rentprice": request.form['rentprice'],
        "containerimg": filename,
        "description": request.form['description'],
        "customers_id": request.form['customers_id']
        }
        container_id = Container.save(data)
        return redirect('/inventory')
    else:
        flash("Allowed image types are png, jpg, jpeg, gif", 'container')
        return redirect('/add/container')

@app.route('/display/<filename>')
def display_image(filename):
	#print('display_image filename: ' + filename)
	return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route('/show/<int:container_id>')
def show(container_id):
    container = Container.get_one_container(container_id)
    return render_template("view.html", container = container )

@app.route('/edit/<int:container_id>')
def editpage(container_id):
    if 'customer_is_admin' not in session:
        return redirect('/inventory')
    container = Container.get_one_container(container_id)
    all_customers = Customer.get_all_customers()
    return render_template("edit.html", container = container, all_customers = all_customers)

@app.route('/edit', methods=['POST'])
def edit():
    if 'customer_is_admin' not in session:
        return redirect('/inventory')

    container = Container.get_one_container(request.form['id'])

    if not Container.validate_container(request.form):
        redirect_url = '/edit/' + request.form['id']
        return redirect(redirect_url)

    print(request.files['containerimg'])
    if request.files['containerimg'].filename == '':
        data = {
        "id": request.form['id'],
        "height": request.form['height'],
        "width": request.form['width'],
        "length": request.form['length'],
        "forsale": request.form['forsale'],
        "saleprice": request.form['saleprice'],
        "forrent": request.form['forrent'],
        "rentprice": request.form['rentprice'],
        "containerimg": container.containerimg,
        "description": request.form['description'],
        "customers_id": request.form['customers_id']
        }
    else:
        newpic = request.files['containerimg']
        if newpic and allowed_file(newpic.filename):
            filename = secure_filename(newpic.filename)
            basedir = os.path.dirname(os.path.dirname(__file__))
            newpic.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename))
            data = {
            "id": request.form['id'],
            "height": request.form['height'],
            "width": request.form['width'],
            "length": request.form['length'],
            "forsale": request.form['forsale'],
            "saleprice": request.form['saleprice'],
            "forrent": request.form['forrent'],
            "rentprice": request.form['rentprice'],
            "containerimg": filename,
            "description": request.form['description'],
            "customers_id": request.form['customers_id']
            }
        else:
            flash("Allowed image types are png, jpg, jpeg, gif", 'container')
            redirect_url = '/edit/' + request.form['id']
            return redirect(redirect_url)

    container_id = Container.edit(data)
    return redirect('/inventory')

@app.route('/delete/<int:container_id>')
def delete(container_id):
    if 'customer_is_admin' not in session:
        return redirect('/inventory')
    Container.delete(container_id)
    return redirect('/inventory')
