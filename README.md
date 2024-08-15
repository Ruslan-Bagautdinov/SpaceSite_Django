# SPACE SITE!
## SPACE SITE! is a FastAPI-based demo site that takes you on a journey through the cosmos. Explore beautiful space images on the home page, manage user profiles, create and edit posts, and administer user data with ease. This application showcases the power and flexibility of FastAPI for building modern web applications.

## Key Features:
- Stunning Space Images: The home page features captivating images of the universe, galaxies, and cosmos, sourced from Unsplash to provide an immersive experience.

- User Management: Register, log in, and manage user profiles with personalized information, including profile pictures and contact details.

- Post Creation and Editing: Users can create, view, edit, and delete posts, making it easy to share thoughts and discoveries.

- Admin Options: Administrators have access to additional buttons to manage users data and users posts.

- Secure and Scalable: Built with security and scalability in mind, leveraging FastAPI's robust middleware and dependency injection systems.

- Two-Role Authentication: Implements a secure authentication system using JWT (JSON Web Tokens) for access and refresh tokens, stored in cookies to enhance security and user experience.

- Async Postgres Database: Utilizes an asynchronous Postgres database for efficient and high-performance data handling, ensuring smooth operations even under high load.

## Routes
Home
- GET /: Home page displaying stunning space images and paginated posts.

Authentication
- POST /register: Register a new user.

- POST /login: Log in an existing user.

- GET /logout: Log out the user.

Profile
- GET /protected/me: Redirect to the user's profile page.

- GET /protected/profile/{user_id}: Display the user's profile page.

- POST /protected/profile/{user_id}/update: Update the user's profile.

- GET /protected/profile/{user_id}/delete: Display the confirmation page for deleting the user's profile.

- POST /protected/profile/{user_id}/delete: Delete the user's profile.

Posts
- GET /posts/all: Retrieve all posts for the authenticated user.

- GET /posts/view/{post_id}: View a specific post by ID.

- GET /posts/new: Display the form to create a new post.

- POST /posts/new: Create a new post.

- GET /posts/edit/{post_id}: Display the form to edit a post.

- POST /posts/edit/{post_id}: Update a post.

- POST /posts/delete/{post_id}: Delete a post.

Admin
- GET /admin/users: Retrieve a list of all users for admin view.

- GET /admin/users/{user_id}/posts: Retrieve posts by a specific user for admin view.

## Installation
Clone the Repository

```bash
git clone https://github.com/Ruslan-Bagautdinov/SpaceSite_FastApi.git
cd SpaceSite_FastApi
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
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_MINUTES=10080
ALGORITHM=HS256

POSTGRES_HOST='localhost'
POSTGRES_PORT='5432'
POSTGRES_DB='fastapi_spacesite_pg'
POSTGRES_USER='postgres'
POSTGRES_PASSWORD='your_postgres_password'

UNSPLASH_ACCESS_KEY='your_unsplash_access_key'
```
Replace your_secret_key, your_postgres data, and your_unsplash_access_key with your actual values.

5. Set Up the Database:
Ensure your PostgreSQL database is running and configured according to the parameters in your '.env' file. Then, run the migrations to set up the database schema:

```bash
alembic upgrade head
```

6. Run the Application:
```bash
uvicorn app.main:app --reload
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
