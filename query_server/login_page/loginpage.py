from flask import Flask, render_template, redirect, url_for, request, session, g
import sqlite3
import json

class User:
    def __init__(self, user_id, username, password):
        self.username = username
        self.password =password
        self.user_id = user_id



#app.run()
#app.run(debug = True)
app.secret_key = 'hjbaslvyiwbeauvywbekuy'

# @app.before_request
# def before_request():
#     if 'user_id' in session:
#         db = sqlite3.connect("user_db.db")
#         db.row_factory = sqlite3.Row
#         cursor = db.execute('select * from users where id=?',(session['user_id'],)) 
#         for row in cursor:    
#             g.user = row['username']
#         #g.user = 'fiubawlibpwiubpiweg'

# # Route for handling the login page logic
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     error = None
#     if request.method == 'POST':
#         session.pop('user_id', None)
#         db = sqlite3.connect("user_db.db")
#         db.row_factory = sqlite3.Row
#         cursor = db.execute('select * from users')
#         for row in cursor:    
#             if request.form['username'] == row['username'] and request.form['password'] == row['password']:
#                 session['user_id'] = row['id']
#                 return redirect(url_for('profile'))
        
#         return 'Invalid Credentials. Please try again.'
#     return render_template('login.html', error=error)






# @app.route('/profile')
# def profile():
#     if not g.user:
#         return redirect(url_for('login'))
#     return #url for dashboard


if __name__ == '__main__':
    # RUN
    app.run()