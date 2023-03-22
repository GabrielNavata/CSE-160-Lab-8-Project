import argparse
from flask import *


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CSE 160 Lab 8 Student Enrollment Web App")
    parser.add_argument("--port", default=5000, type=int)
    args = parser.parse_args()

    app.run(host="0.0.0.0", port=args.port, debug = True)  