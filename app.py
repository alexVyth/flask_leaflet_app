from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://alex@localhost/geo'
db = SQLAlchemy(app)
db.Model.metadata.reflect(db.engine)


class Records(db.Model):
    __tablename__ = 'records'
    __table_args__ = {'extend_existing': True}
    identifier = db.Column(db.Text, primary_key=True)


@app.route('/')
def hello_world():
    return render_template("index.html", layer='annual_temp')


if __name__ == '__main__':
    app.run(debug=True)
