from flask import Flask
from website.app import create_app
import sys


app=create_app()

if __name__ == "__main__":
    app.run(debug=True)

