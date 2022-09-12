# MSc Computer Science Project 2021-22: Nathaniel Samson

### Overview

This repo defines a language-learning web app intended to promote the memorisation of vocabulary terms using spaced-repetition.

The app is designed to complement classroom-based teaching by providing tools for both teachers and their students:

* For **teachers**, the app tracks the progress of all students in their class, helping to identify any subject areas that may need further reinforcement. 
* For **students**, the app delivers multiple-choice quizzes, tailored to the individual and scheduled according to the principles of spaced repetition, making learning both enjoyable and efficient.

***

### Installation Guide

Navigate to your desired directory and clone the GitHub repo:

    git clone https://github.com/Birkbeck/msc-computer-science-project-2021_22-nat-samson.git

Enter the project directory, set up and activate the virtual environment:

    cd msc-computer-science-project-2021_22-nat-samson
    python3 -m venv venv
    source venv/bin/activate

Ensure that `(venv)` appears in the command prompt, then install the project requirements:

    pip install -r requirements.txt

Set up the environment variables using the supplied defaults (please note, this includes a demo `SECRET_KEY` for convenience, please replace this with your own if desired).

    cp .env.example .env

Set up the database:

    python manage.py migrate

Everything is now installed, but there is no data in the database. I have supplied some example `Word`, `Topic` and `User` data to demonstrate the application’s features. Load the fixture:

    python manage.py loaddata demo.json

Next, you can simulate all the students taking 32 days’ worth of quizzes (you can specify any number of days, but please note larger numbers will take longer to process). 

This command will confirm that the data has been successfully created once it finishes executing:

    python manage.py generate_results 32

Run the server (input _CTRL+C_ in the terminal at any time to stop the server):

    python manage.py runserver

Open the below URL in your preferred web browser:

<http://localhost:8000/>

Please note the following section for instructions on how to log in as existing users and take advantage of the supplied demo data.

***

### User Guide

When attempting to create a new teacher account, you will need to input the _site-code_. This is set in your installation’s `.env` file, and is by default set to: **birkbeck**

As well as creating your own account and using the application that way, you may wish to log in as a teacher or student with existing demo data. These have the following credentials:

* Student usernames are **student1**, **student2**, **student3** etc.
* Teacher usernames are **teacher1**, **teacher2**
* All user passwords are set to **default123**

Please explore the application as both a student and a teacher to see all the features as described in the report.

Additionally, you may wish to log in as an admin. To do so, you will need to create a _superuser_ account using the command line. Stop the server if it is running, then input the below and follow the prompts as follows:

    python manage.py createsuperuser
    Username: [input your desired username]
    Is teacher: True
    Password: [input your desired password]
    Password (again): [repeat your desired password]

The application will treat the admin as a teacher (assuming you inputted `True` as above). Admins additionally can access the administrative dashboard by visiting the below URL:

<http://localhost:8000/admin/>
