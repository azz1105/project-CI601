import os
import phishing_detection
from flask import Flask, render_template,request
from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for, abort)
from flask import jsonify
from werkzeug.utils import secure_filename
import requests
import smtplib, ssl


app = Flask(__name__)

SITE_KEY = "6LduV5slAAAAAEnuy968qnASLWOWdwDzvsvo5_fL"
SECRET_KEY = "6LduV5slAAAAALYl476hGBj7Cybl5BWX2qFhmBDQ"
VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"
verify_response = None




UPLOAD_FOLDER= '/files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','py'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/result', methods = ['GET', 'POST'])
def result():
    global verify_response
    print(request.form)
    print(request.args)
    if request.method == "GET":
        urlname  = request.args['name']
        result  = phishing_detection.getResult(urlname)
        return result
    else:
        
        secret_response = request.form["g-recaptcha-response"]
        
        verify_response = requests.post(url=f"{VERIFY_URL}?secret={SECRET_KEY}&response={secret_response}").json()
        
        print("#########", verify_response)
        
        if verify_response["success"] == False or verify_response["score"] < 0.5:
            abort(401)
        
        urlname  = request.form['name'].strip()
        if urlname != "":
            result  = phishing_detection.getResult(urlname)
        else:
            result = "invalid URL"
        result_color = "success" if "Legitimate" in result else "danger"
        return render_template("getInput.html", result=f"This is a {result}", site_key=SITE_KEY, result_color=result_color)

# @app.route('/upload')
# def upload():
# 	return 'yes'

@app.route('/', methods = ['GET', 'POST'])
def hello():
	if request.method == 'POST':
		if 'file' not in request.files:
			flash('no file part')
			return "false"
		file = request.files['file']
		if file.filename == '':
			flash('no select file')
			return 'false'
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			contents = file.read()
			with open("files/URL.txt","wb") as f:
				f.write(contents)
			file.save = (os.path.join(app.config['UPLOAD_FOLDER'], filename))
			return render_template("getInput.html")
	return  render_template("getInput.html", site_key=SITE_KEY)



@app.route('/hints', methods = ['GET'])
def hints():
    return  render_template("hints.html")


@app.route('/contact', methods = ['GET'])
def contact_get():
    return  render_template("Contact.html")

@app.route('/contact', methods = ['POST'])
def contact_post():
    
    name = request.form["name"]
    visitor_email = request.form["Email"]
    message = request.form["message"]
    
    email_from = 'aziz.aljehani99@gmail.com'
    
    email_subject = "New form submission"
    
    email_body = f"User Name: {name}.\n" + \
 					f"User Email: {visitor_email}.\n" + \
 						f"User Message: {message}.\n"
 
    to = "aziz.aljehani99@gmail.com"
    
    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls
    sender_email = "azizalje2@gmail.com"
    password = "Hubhet4v"
    
    # Create a secure SSL context
    context = ssl.create_default_context()


    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server,port)
        server.ehlo() # Can be omitted
        server.starttls(context=context) # Secure the connection
        server.ehlo() # Can be omitted
        server.login(sender_email, password)
        # TODO: Send email here
        server.sendmail(sender_email, sender_email, email_body)
        flash("email sent")
    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        server.quit()


    return render_template("Contact.html")





if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
