from flask import Blueprint, Response, request
from http import HTTPStatus
from typing import List, Dict
import sys

from news_finder.db import get_db
from news_finder.response import (
    make_response_from_error,
    ErrorKind,
    make_success_response,
)



