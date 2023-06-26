from flask_app import app
from flask import render_template,redirect,request,session,flash
from flask_app.models.customer import Customer
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
bcrypt = Bcrypt(app)


app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'stopthecheat@gmail.com'
app.config['MAIL_PASSWORD'] = '****'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)


@app.route("/")
def index():
    return render_template("index.html")

@app.route('/register', methods=['POST'])
def register():
    if not Customer.validate_registration(request.form):
        return redirect('/')
    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    data = {
    "firstname": request.form["firstname"],
    "lastname" : request.form["lastname"],
    "email" : request.form["email"],
    "password" : pw_hash,
    }
    customer_id = Customer.save(data)
    session['customer_id'] = customer_id
    session['customer_name'] = request.form["firstname"]
    session['customer_email'] = request.form["email"]
    return redirect('/inventory')

@app.route('/changepassword', methods=['POST'])
def changepassword():
    if 'customer_id' not in session:
        return redirect('/inventory')
    data = { "id" : session['customer_id'] }
    customer_in_db = Customer.get_customer_by_id(data)
    if not customer_in_db:
        flash("You are not properly logged in yet.", 'login')
        return redirect("/")
    if not bcrypt.check_password_hash(customer_in_db.password, request.form['password']):
        flash("Invalid Old Password", 'password_change')
        return redirect('/inventory')
    if not Customer.validate_passwordchange(request.form):
        return redirect('/inventory')
    pw_hash = bcrypt.generate_password_hash(request.form['newpassword'])
    newdata = {
    "id": session["customer_id"],
    "password": pw_hash,
    }
    customer_id = Customer.update(newdata)
    flash("Your Password has been changed", 'password_change')
    return redirect("/inventory")

@app.route('/login', methods=['POST'])
def login():
    data = { "email" : request.form["email"] }
    customer_in_db = Customer.get_customer_by_email(data)
    if not customer_in_db:
        flash("A customer with this email address does not exist. Please register first.", 'login')
        return redirect("/")
    if not bcrypt.check_password_hash(customer_in_db.password, request.form['password']):
        flash("Invalid Password", 'login')
        return redirect('/')
    session['customer_id'] = customer_in_db.id
    session['customer_name'] = customer_in_db.firstname
    session['customer_email'] = customer_in_db.email
    if customer_in_db.isadmin == True:
        session['customer_is_admin'] = customer_in_db.isadmin
    return redirect("/inventory")

@app.route('/logout')
def logout():
    session.clear()
    return redirect ('/')

@app.route('/sendmail', methods=['POST'])
def sendmail():
    customeremail = request.form['customeremail']
    currentrenter = request.form['currentrenter']
    containerid = request.form['containerid']
    customer = Customer.get_customer_by_email(customeremail)
    customername = customer.firstname + " " + customer.lastname
    emailmsg = 'Inquiry Regarding Container ' + containerid + ': \n' + 'Customer Name: ' + customername + '\n' + 'Customer Email: ' + customeremail + '\n' + request.form['msg']
    if currentrenter == 1:
        emailsubject = 'Request from Current Renter ' + customername + ' Regarding Container ' + containerid 
    else:
        emailsubject = 'Container Inquiry from ' + customername + ' Regarding Container ' + containerid

    msg = Message(subject=emailsubject, sender=customeremail, reply_to=customeremail, recipients=['mybrothersemailaddress@example.com'])
    msg.body = emailmsg
    mail.send(msg)
    flash("Message sent!", 'email')
    return redirect ('/inventory')