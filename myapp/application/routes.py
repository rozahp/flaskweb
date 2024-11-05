from flask import current_app as app, render_template

@app.route('/', methods=['GET'])
def index():
    """ index route."""
    return render_template('home.html', title="MyApp")

