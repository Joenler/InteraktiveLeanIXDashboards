from flask import Flask, redirect, url_for, render_template
import plotly as px


app = Flask(__name__)

@app.route("/")
def home():
    # noinspection PyUnresolvedReferences
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
