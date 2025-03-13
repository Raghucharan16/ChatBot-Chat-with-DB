from vanna.flask import VannaFlaskApp
from vanna.remote import VannaDefault
from dotenv import load_dotenv
import flask
from flask import make_response
from vanna.flask.auth import AuthInterface
import os

# Load environment variables
load_dotenv()
api_key = os.getenv('VANNA_API_KEY')
vanna_model_name = os.getenv('VANNA_MODEL')
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_port = os.getenv("DB_PORT", "5432")  # Default to 5432 if not set

# Initialize Vanna
vn = VannaDefault(model=vanna_model_name, api_key=api_key)
vn.connect_to_postgres(
    host=db_host,
    dbname=db_name,
    user=db_user,
    password=db_password,
    port=db_port
)

class SimplePassword(AuthInterface):
    def __init__(self, users: list):
        """
        Authentication with a simple email-password dictionary.
        """
        self.users = users  # Store users as a list of dictionaries

    def get_user(self, flask_request) -> any:
        """
        Retrieve the logged-in user from the cookie.
        """
        return flask_request.cookies.get('user')  # Get user email from cookie

    def is_logged_in(self, user: any) -> bool:
        """
        Check if the user is logged in.
        """
        return user is not None

    def override_config_for_user(self, user: any, config: dict) -> dict:
        """
        Customize the config for the logged-in user.
        """
        return config

    def login_form(self) -> str:
        """
        Render the login form with FreshBus branding.
        """
        return '''
        <div class="p-4 sm:p-7">
            <div class="text-center">
                <img src="https://public.freshbus.com/logo_blue.png" alt="FreshBus Logo" class="mx-auto mb-4 h-16">
                <h1 class="block text-2xl font-bold text-gray-800 dark:text-white">FreshBus Epicenter</h1>
            </div>
            <div class="mt-5">
                <form action="/auth/login" method="POST">
                    <div class="grid gap-y-4">
                        <div>
                            <label for="username" class="block text-sm mb-2 dark:text-white">Username</label>
                            <div class="relative">
                                <input type="text" id="username" name="username"
                                    class="py-3 px-4 block w-full border border-gray-200 rounded-lg text-sm
                                    focus:border-blue-500 focus:ring-blue-500 dark:bg-slate-900 dark:border-gray-700
                                    dark:text-gray-400 dark:focus:ring-gray-600"
                                    required>
                            </div>
                        </div>
                        <div>
                            <label for="password" class="block text-sm mb-2 dark:text-white">Password</label>
                            <div class="relative">
                                <input type="password" id="password" name="password"
                                    class="py-3 px-4 block w-full border border-gray-200 rounded-lg text-sm
                                    focus:border-blue-500 focus:ring-blue-500 dark:bg-slate-900 dark:border-gray-700
                                    dark:text-gray-400 dark:focus:ring-gray-600"
                                    required>
                            </div>
                        </div>
                        <button type="submit" class="w-full py-3 px-4 inline-flex justify-center items-center
                            gap-x-2 text-sm font-semibold rounded-lg border border-transparent bg-blue-600 text-white
                            hover:bg-blue-700">Sign in</button>
                    </div>
                </form>
            </div>
        </div>
        '''

    def login_handler(self, flask_request) -> str:
        """
        Handle login. This is invoked when the user submits the login form.
        """
        if flask_request.method != "POST":
            return "Invalid request method", 405  # Ensure it's a POST request

        # Ensure 'username' and 'password' exist in the form data
        username = flask_request.form.get('username')
        password = flask_request.form.get('password')

        if not username or not password:
            return "Missing username or password", 400  # Return Bad Request if missing

        # Check if the username exists and the password matches
        if any(user["username"] == username and user["password"] == password for user in self.users):
            response = flask.make_response(flask.redirect('/'))  # Redirect to the main app
            response.set_cookie('user', username)  # Store the username in a cookie
            return response

        return 'Login failed', 401  # Unauthorized access


    def callback_handler(self, flask_request) -> str:
        """
        Handle authentication callbacks.
        """
        user = flask_request.args['user']
        response = make_response('Logged in as ' + user)
        response.set_cookie('user', user)
        return response

    

    def logout_handler(self, flask_request) -> str:
        """
        Handle logout. Remove the user cookie and redirect to login.
        """
        response = make_response(flask.redirect('/auth/login'))
        response.delete_cookie('user')  # Clear the user cookie
        return response

# Create Flask app with Vanna
app = VannaFlaskApp(
    vn,
    title="FreshBus GenAI",
    subtitle="Your AI assistant at FreshBus",
    logo="https://public.freshbus.com/logo_blue.png",
    allow_llm_to_see_data=False,
    sql=False,
    csv_download=False,
    summarization=False,
    followup_questions=False,
    show_training_data=False,
    auth=SimplePassword(users=[
        {"username": "freshbus-genai", "password": "Fm4kP2A8mhqDuF4"},
        {"username": "saikiran", "password": "CeA5LbslAueV1Xh"},
        {"username": "rohit", "password": "12345321"},
        {"username": "karthik", "password": "Aen2yQteufDVEry"},
        {"username": "geetanvesh", "password": "ZZOJy9ll2Pn375t"},
        {"username": "vasant", "password": "O0QiypCyKF7Lr9m"},
        {"username": "haritha", "password": "q1q9jeYnecnyaFj"}
    ])
)

# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
