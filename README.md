# msc-computer-science-project-2021_22-nat-samson
msc-computer-science-project-2021_22-nat-samson created by GitHub Classroom

Steps to make local version:

Clone the repo:

```git clone https://github.com/Birkbeck/msc-computer-science-project-2021_22-nat-samson.git```

Create a virtual environment, and verify it has been activated:

```virtualenv venv -p python3```

Install the required packages (which includes Django itself):

```pip install -r requirements.txt```

Set up the required environment variables. The easiest way is to copy and rename the supplied .env.example file using:

```cp .env.example .env```

And within your .env file, you must specify a Secret Key:

```TODO: secret key generation advice```

Create the DB (here using SQLite for development purposes):

```python manage.py migrate```

Run the server:

```python manage.py runserver```

Visit the running web application your preferred web browser:

[Open in web browser.](http://localhost:8000/)



