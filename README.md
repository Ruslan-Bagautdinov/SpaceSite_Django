# SPACE SITE!
## SPACE SITE! is a Django-based demo site that takes you on a journey through the cosmos. Explore beautiful space images on the home page, manage user profiles, create and edit posts, and administer user data with ease. This application showcases the power and flexibility of Django for building modern web applications.

## Key Features:
- Stunning Space Images: The home page features captivating images of the universe, galaxies, and cosmos, sourced from Unsplash to provide an immersive experience.

- User Management: Register, log in, and manage user profiles with personalized information, including profile pictures and contact details.

- Post Creation and Editing: Users can create, view, edit, and delete posts, making it easy to share thoughts and discoveries.

- Admin Options: Administrators have access to additional buttons to manage users data and users posts.

- Secure and Scalable: Built with security and scalability in mind, leveraging Django's robust middleware and authentication systems.

- Two-Role Authentication: Implements a secure authentication system using Django's built-in authentication for access and refresh tokens.

- Async Postgres Database: Utilizes an asynchronous Postgres database for efficient and high-performance data handling, ensuring smooth operations even under high load.

## Installation
Clone the Repository

```bash
git clone https://github.com/Ruslan-Bagautdinov/SpaceSite_Django.git
cd SpaceSite_Django
```

### Install with Docker

```bash
docker-compose up --build
```


### Install without Docker

1. Clone the Repository:

```bash
git clone https://github.com/Ruslan-Bagautdinov/SpaceSite_FastApi.git
cd SpaceSite_FastApi
```
2. Create a Virtual Environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```
3. Install Dependencies:
```bash
pip install -r requirements.txt
```
4. Create a '.env' File:
Create a '.env' file in the root directory of the project and fill in the necessary values. You can use sample.env as a template. Here is an example of what the .env file should look like:
```dotenv
SECRET_KEY='your_secret_key'
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

UNSPLASH_ACCESS_KEY='your_unsplash_access_key'
```
Replace 'your_secret_key' and 'your_unsplash_access_key' with your actual values.

5. Set Up the Database:
Run the migrations to set up the database schema:

```bash
python manage.py migrate
```

6. Add Test Users:
Run the migrations to set up the database schema:

```bash
python manage.py add_test_users
```


7. Run the Application:
```bash
python manage.py runserver
```

## Users

Two test users are added to the database. Their login information is as follows:

#### Admin User:
- Username: 
```
admin
```
- Password: 
```
123
```
#### Regular User:
- Username: 
```
user
```
- Password: 
```
123
```

Your application should now be running locally. You can access it at http://localhost:8000

## License
This project is currently unlicensed and free to use.
