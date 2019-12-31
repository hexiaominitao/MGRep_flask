from flask import (Blueprint, jsonify, request)
from flask_cors import CORS

api = Blueprint('api_v0', __name__, url_prefix="/api")
CORS(api)

import app.api.urls
