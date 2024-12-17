from flask import Flask, render_template

app = Flask(__name__)

@app.errorHandler(404)
def page_not_found():
    return render_template('/index.html'), 404