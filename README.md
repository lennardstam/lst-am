# lst.am

#### Overview

lst.am is an self hosted URL shortener made in Flask.

#### Demo

[demo.lst.am](https://demo.lst.am/)   
_Database will be restored daily._  

Username: `admin@lst.am`  
Password: `admin`   

![Screenshot](screenshot.gif)

#### Features

  * URL shortener
  * Customized short URL's and length
  * Link visit stats
  * User links overview 
  * Admin panel for user management
  * Password recovery	
	
#### Technical Info

  * Python 3, Javascript, JQuery, HTML, CSS
  * Framework: Flask
  * DB: SQLite
  * Libs: SQLAlchmey, JWT
  * Docker
  * Docker-compose

#### Configuration

Update settings.py with your own mail server and MySQL credentials.

#### Installation/Setup

**Docker**

Clone `git clone https://github.com/lennardstam/lst-am.git` & `cd lst-am`  
Build the image `docker build /path/to/lst-am/ -t lst-am`  
To run the container: `docker run -it -p 5000:5000 lst-am`.  
For docker-compose, run `docker-compose up -d`  

**Manual**(from source)

Clone `git clone https://github.com/lennardstam/lst-am.git` & `cd lst-am`  
(Optional) `Install virtualenv` (optional but recommended)  
	`virtualenv -p python3 env`  
	`source env/bin/activate`  
Install dependencies: `pip3 install -r requirements.txt`  
`python3 run.py` (It runs Flask app using Werkzeug. Gunicorn not yet added)  

**Access**

Visit `127.0.0.1:5000` in your browser to use the app  
Use the following credentials:  
Username: `admin@lst.am`  
Password: `admin`  
    

#### Notes

This project is in early development. Therefore features and configuration settings are limited  
Logging is not yet available.  
Role based user access is static. User with id 1, is admin.  
Guest usage is not possible yet
