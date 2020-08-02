# Encryptid '20
The platform for Encryptid '20 built using Django, PostgreSQL, and Firestore.<br/>
Check out the concept [here](https://ctrl.gq/encryptid/format).

### Setup
1. Set up a virtual environment and install all the requirements from `requirements.txt`
```
py -3 -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

2. Create a Firebase project and activate the Firestore DB.<br/>Download the project's service account credentials and populate it in a `.env`

3. Make the necessary migrations using `python manage.py migrate`

4. Run the server on port 8000 using `python manage.py runserver`
