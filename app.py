from flask import Flask, render_template

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def index():

    return render_template("index.html")

@app.route('/admissions')
def admissions():
    return render_template("admissions.html")

@app.route('/add_admission')
def add_admission():
    return render_template('add_admission.html')

if __name__ =="__main__":
    app.run(debug=True)