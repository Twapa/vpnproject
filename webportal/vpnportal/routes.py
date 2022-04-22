from vpnportal import app
from flask import render_template, redirect, url_for, flash,request
from vpnportal.models import Ipsec, Item, User
from vpnportal.forms import RegisterForm, LoginForm
from vpnportal import db
from flask_login import login_user, logout_user, login_required
import json

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')





@app.route('/serverroute/<int:id>')
@login_required
def serverroute(id):
    
    mydata = Ipsec.query.get(id)

    return render_template('server.html',data=mydata)

@app.route('/servermetrics')
@login_required
def servermetrics():
    

    return render_template('servermetrics.html') 

@app.route('/serverconfig')
@login_required
def serverconfig():
    

    return render_template('serverconfig.html')




@app.route('/htmlvue')

def vuerender():
    

    return render_template('htmlvue.html')    




    


@app.route('/json')
@login_required
def savejson():
    with open('./vpnportal/data.json','r') as f:
        data = json.loads(f.read())

        return data


@app.route('/servers')
@login_required
def webportal_page():
    all_data = Ipsec.query.all()
    return render_template('servers.html',ipsec = all_data)

    

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('home_page'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('home_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))


#this route is for inserting data to sql database via html forms
@app.route('/insert', methods = ['POST'])
def insert():
 
    if request.method == 'POST':
 
        vpnaddress = request.form['vpnaddress']
        vpnusername = request.form['vpnusername']
        vpnpassword = request.form['vpnpassword']

        sshaddress = request.form['ipsecaddress']
        sshusername = request.form['ipsecusername']
        sshpassword = request.form['ipsecpassword']
 
 
        vpnserverdata = Ipsec(vpnaddress, vpnusername,vpnpassword,sshaddress,sshusername,sshpassword)
        db.session.add(vpnserverdata)
        db.session.commit()
 
        flash("Server Inserted Successfully")
 
        return redirect(url_for('webportal_page'))




#this is our update route where we are going to update our employee
@app.route('/update', methods = ['GET', 'POST'])
def update():
 
    if request.method == 'POST':
        my_data = Ipsec.query.get(request.form.get('id'))

        my_data.vpnaddress = request.form['vpnaddress']
        my_data.vpnusername = request.form['vpnusername']
        my_data.my_vpnpassword = request.form['vpnpassword']

        my_data.sshaddress = request.form['sshaddress']
        my_data.sshusername = request.form['sshusername']
        my_data.sshpassword = request.form['sshpassword']
 
        db.session.commit()
        flash("Server Updated Successfully")
 
        return redirect(url_for('webportal_page'))
 
 
 
 
#This route is for deleting our employee
@app.route('/delete/<id>/', methods = ['GET', 'POST'])
def delete(id):
    my_data = Ipsec.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash("Server Deleted Successfully")
 
    return redirect(url_for('webportal_page'))
 
 

 










