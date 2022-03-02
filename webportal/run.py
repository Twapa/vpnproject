from vpnportal import app

#Checks if the run.py file has executed directly and not imported
if __name__ == '__main__':
    # app.run(host='192.168.42.10',port=500)
    app.run(debug=True)
    