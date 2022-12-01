from flask import Flask, render_template

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def index():

    return render_template("index.html")

@app.route('/admissions_history')
def admissions_history():
    return render_template("admissions_history.html")

@app.route('/add_admission')
def add_admission():
    return render_template('add_admission.html')

@app.route('/admission')
def admission():
    return render_template("admission.html")

if __name__ =="__main__":
    app.run(debug=True)