# import dependencies 
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Set the environment variable to specify the app to run
# os.environ['FLASK_APP'] = 'app.py'

# Run the Flask application
# subprocess.Popen(['flask', 'run'])

#################################################
# Database Setup
#################################################
engine = create_engine("/Users/jessicamaranto/Desktop/DataBootcamp/sqlalchemy-challenge/SurfsUp/Hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return jsonify({
        "Available Routes": [
            "/api/v1.0/precipitation",
            "/api/v1.0/stations",
            "/api/v1.0/tobs",
            "/api/v1.0/<start>",
            "/api/v1.0/<start>/<end>"
        ]
    })

@app.route("/api/v1.0/precipitation")
def precipitation():
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date_point = recent_date[0]
    year_ago_date = pd.to_datetime(recent_date_point) - pd.DateOffset(years=1)
    year_ago_date_str = year_ago_date.strftime('%Y-%m-%d')
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago_date_str).all()
    precipitation_data = {date: prcp for date, prcp in results}
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def tobs():
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date_point = recent_date[0]
    year_ago_date = pd.to_datetime(recent_date_point) - pd.DateOffset(years=1)
    year_ago_date_str = year_ago_date.strftime('%Y-%m-%d')

    results = session.query(Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= year_ago_date_str).all()
    tobs_list = [tob[0] for tob in results]
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start(start):
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).all()
    return jsonify({
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    })

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    results = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    return jsonify({
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    })

if __name__ == "__main__":
    app.run(debug=True)
