# Self Service Portal
This folder contains the webapplication files for the self service portal, including a Django backend and an Angular frontend.

## Backend: Python Django

### Initiate Django project

```
python -m venv venv
source venv/bin/activate

pip install django

django-admin startproject backend

cd backend
python manage.py startapp api

python manage.py migrate

python manage.py runserver

pip install gunicorn
pip install dj-database-url
pip install whitenoise
pip install psycopg2-binary
pip install djangorestframework

python manage.py createsuperuser --email admin@selfservciceportal.de --username admin

```

### Enable CORS
https://github.com/adamchainz/django-cors-headers#setup

### Enable Keycloak SSO Authentication
https://django-keycloak.readthedocs.io/en/latest/index.html

### Enable OIDC Token Verification & Authentication for consumable API
"JWT tokens will be validated against the public keys of an OpenID connect authorization service. Bearer tokens are used to retrieve the OpenID UserInfo for a user to identify him." (https://github.com/ByteInternet/drf-oidc-auth)

## Frontend: Angular 

### Dependencies
The following packages need to be installed on the node that runs the frontend:

* Node.js (tested version: v12.18.3) & npm (tested version: 6.14.6)
    * Add the PPA: `curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -`
    * Install nodejd & npm: `sudo apt install nodejs`
* Angular CLI (tested version: 10.0.4)
    * `(sudo) npm install -g @angular/cli` 

### Initiate Angular project

```
npm install -g @angular/cli

ng new frontend

cd frontend/
ng serve

ng build
```