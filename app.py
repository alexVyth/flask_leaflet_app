from flask import Flask, render_template, request, redirect, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, StringField, SelectField
from flask_table import Table, Col, LinkCol
import cv2
import urllib.request
import numpy as np


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://alex@localhost/geo'
app.secret_key = "not a secret"

db = SQLAlchemy(app)
db.Model.metadata.reflect(db.engine)


def canny(url):
    url = urllib.request.urlopen(url)
    img = np.asarray(bytearray(url.read()), dtype=np.uint8)
    decoded = cv2.imdecode(img, -1)
    gray = cv2.cvtColor(decoded, cv2.COLOR_BGR2GRAY)
    edge = cv2.Canny(gray, 50, 20)
    print(edge.shape)
    _, encoded = cv2.imencode(".png", edge)
    return encoded


def get_map_builder(layer):
    url = "http://localhost:8080/geoserver/ows?service=WMS" +\
          "&version=1.3.0&request=GetMap&layers=" +\
          layer + "&width=720&height=360&format=image/png&bbox=-180,-90,180,90"
    return url


class Results(Table):
    classes = ["table"]
    identifier = Col('identifier', show=False)
    title = Col('title')
    date = Col('date')
    type = Col('type')
    source = Col('source')
    crs = Col('crs')
    geotiff = LinkCol('GeoTIFF', 'geotiff',
                      url_kwargs=dict(identifier='identifier'))


class SearchForm(Form):
    choices = [('Title', 'Title'),
               ('Date', 'Date'),
               ('Type', 'Type'),
               ('CRS Code', 'CRS Code'),
               ('Source', 'Source')]
    select = SelectField('Search Field:', choices=choices)
    search = StringField('')


class Records(db.Model):
    __tablename__ = 'records'
    __table_args__ = {'extend_existing': True}
    identifier = db.Column(db.Text, primary_key=True)


@app.route('/')
@app.route('/view')
@app.route('/view/annual')
def annual():
    return render_template("view.html",
                           service="view", service_type="annual")


@app.route('/view/monthly')
def monthly():
    return render_template("view.html",
                           service="view", service_type="monthly")


@app.route('/process')
def process():
    return render_template("process.html", service="process")


@app.route('/process_temp')
def process_temp():
    buff = canny(get_map_builder("annual_temp"))
    response = make_response(buff.tobytes())
    response.headers["Content-Type"] = 'image/png'
    return response


@app.route('/process_hum')
def process_hum():
    buff = canny(get_map_builder("annual_hum"))
    response = make_response(buff.tobytes())
    response.headers["Content-Type"] = 'image/png'
    return response


@app.route('/process_prec')
def process_prec():
    buff = canny(get_map_builder("annual_prec"))
    response = make_response(buff.tobytes())
    response.headers["Content-Type"] = 'image/png'
    return response


@app.route('/download', methods=["GET", "POST"])
def download():
    search = SearchForm(request.form)
    if request.method == "POST":
        return search_results(search)
    return render_template("download.html", service="download", form=search)


@app.route('/results')
def search_results(search):
    results = []
    search_string = search.data['search']
    if search_string:
        if search.data['select'] == 'Title':
            qry = Records.query.filter(Records.title.contains(search_string))
            results = qry.all()
        elif search.data['select'] == 'Date':
            qry = Records.query.filter(Records.date.contains(search_string))
            results = qry.all()
        elif search.data['select'] == 'Type':
            qry = Records.query.filter(Records.type.contains(search_string))
            results = qry.all()
        elif search.data['select'] == 'Source':
            qry = Records.query.filter(Records.source.contains(search_string))
            results = qry.all()
        elif search.data['select'] == 'CRS Code':
            qry = Records.query.filter(Records.crs.contains(search_string))
            results = qry.all()
        else:
            results = Records.query.all()
    else:
        results = Records.query.all()
    if not results:
        flash('No results found!')
        return redirect('/download')
    else:
        table = Results(results)
        table.border = True
        return render_template('results.html', table=table)


@app.route('/geotiff/<string:identifier>')
def geotiff(identifier):
    qry = Records.query.filter(Records.identifier == identifier)
    result = qry.first()
    if result:
        if "annual" in result.title:
            ref = "http://localhost:8080/geoserver/ows?service=WCS&version=2.0.1&request=GetCoverage&format=image/geotiff&"
            ref += "CoverageID=" + result.title
        else:
            ref = "http://localhost:8080/geoserver/ows?service=WCS&version=2.0.1&request=GetCoverage&format=image/geotiff&"
            ref += "CoverageID=" + result.title + "&"
            ref += "time=" + result.date
        return redirect(ref)



if __name__ == '__main__':
    app.run(debug=True)
