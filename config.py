# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

# Define the template directory
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates/')

# Define the static directory
STATIC_DIR = os.path.join(BASE_DIR, 'static/')

# Define the upload directory & support video format
UPLOAD_DIR = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = set(['mov', 'avi', 'mp4', 'webm'])