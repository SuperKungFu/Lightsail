# Introduction
Udacity backend project for an item catalog.

# Contents
* application.py - the main Python flask web server
* models.py - DB object definitions
* catalog_loader.py - utility script to pre-load a few items
* client_secret.json - Google API keys
* static directory - CSS files
* templates directory - various HTML templates for the application

# How to run
* Load up vagrant
* If you wish to load some items run from the command line: python catalog_loader.py
* From command line run: python application.py
* The web server will run on http://localhost:8000/

# Acknowledgements
* Oath code is mostly from the class notes and lessons
