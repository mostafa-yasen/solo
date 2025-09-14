#!/bin/sh

# This script runs database migrations and then starts the Flask application.

flask db upgrade

flask run --host 0.0.0.0
