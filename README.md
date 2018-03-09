# QuizMaker
An interactive way to make and take quizes.

## Module Requirements
Note: Apply sudo if required for your system.

Install the required packages by running:

```
pip install -r requirements.txt
```

## Installation
1. Clone this repository.

2. Make local.py inside settings directly. Copy base.py and paste it into local.py.

3. Create an S3 bucket and fill revelant fields in local.py.

5. Create an API for Google Recaptcha and fill revelant fields in local.py.

6. Create Sengrid API key and fill revelant fields in local.py.

7. Run ''' python manage.py migrate''' when you are in home folder of project.

8. Run ''' python manage.py runserver '''.

9. Create a superuser using '''python manage.py createsuper'''.

10. Open the browser and go to the URL -

    `http://localhost:8000/admin`


11. Login as an admin using superuser credentials.

12. Setup Django-allauth from documentation.

13. Done. :smile:

## Project Dependencies

QuizMaker is built on the [Django Web Framework](https://www.djangoproject.com/), which is a Python based MVC framework. It uses [Django-allauth](https://django-allauth.readthedocs.io/en/latest/) for social login using Facebook and Google.

## Contribute

1. Fork the repository
2. Clone your forked repository
3. Solve the bug or enhance the code and send a Pull Request!
4. I will review it as soon as possible.

## Contact

  > Feedback : Goto 'qzmaker.herokuapp.com' and then click on 'Give your feedback'.

  > Email: harshavardhana.619@gmail.com