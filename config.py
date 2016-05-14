# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  

# Define the template directory
TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates/'),
)

# Define the static directory
STATIC_DIRS = (
	os.path.join(BASE_DIR, 'static/'),
)