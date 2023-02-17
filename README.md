# Introduction
htmx demo sites created for a conference talk titled "Interactive web pages with Django or Flask, without writing JavaScript"

# Set up - data
As far as I know there are no limitations on the use of the data which you need for this website. However, to be on the safe side, I have not included it in the repository.

To get the data:
- Download it from https://www.kaggle.com/datasets/kjanjua/jurassic-park-the-exhaustive-dinosaur-dataset (you may need to create an account first. AFAIK accounts are free)
- Expand (unzip) the file and store the 'data.csv' file in (project-root)/data/data.csv
- You may need to fix the data. When I loaded the spreadsheet in LibreOffice Calc, and in Python's csv module, one cell was missing. This may also be fixed by changing the csv reader settings in the import scripts. I did not try this myself. Look in the row for 'hagryphus' and give it a random period

# Requirements
- The requirements.txt file contains the requirements both the Django and the Flask version
- For Django you probably only need (but I haven't tested this):
  - Django
  - Bokeh
- For Flask you probably only need (also not tested):
  - Flask 
  - Flask-Migrate
  - Flask-SQLAlchemy
  - Bokeh
  - python-dotenv
- 
I developed this with Python 3.10 but it probably works in Python 3.6 or higher

# Django and Flask website
- Make sure you've got the data.csv file, as per the instructions above
- From https://bulma.io/ get bulma.css and store it in (project root)/dinosaurs/static/css
- From https://unpkg.com/browse/htmx.org@1.8.5/dist/ (main/documentation website: https://htmx.org/) get htmx.min.js and store it in (project root)/dinosaurs/static/js
- From https://github.com/SortableJS/Sortable get Sortable.js and store it in (project root)/dinosaurs/static/js
- (optional) Download a dinosaur picture and store it as (project root)/dinosaurs/images/dinosaurs.png
  - Note: I used a premium image from https://www.freepik.com/, under my premium annual plan
- (optional) Create a virtual environment and activate it
- In project root
  - pip install -r requirements.txt

# Django website
- Make sure you've followed the instructions under "Django and Flask website"
- In top 'animals' folder
  - Create the database: python manage.py migrate
  - Import the data: python manage.py import_data
  - Run the server: python manage.py runserver
- In your browser, go to http://127.0.0.1:8000/

# Flask website
- In 'animals_flask' folder
  - Create the database: flask db upgrade
  - Import the data: python import_data.py 
  - Run the server: flask run
- In your browser, go to http://127.0.0.1:5000/
