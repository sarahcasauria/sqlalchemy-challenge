import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables.
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

##################
# Homepage
##################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (f"Welcome to the Hawaii Weather API! Here are a list of available routes:<br/><br/>"
            f"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a> will list all precipitation measurements between 2016-08-23 and 2017-08-23.<br/><br/>"
            f"<a href='/api/v1.0/station'>/api/v1.0/station</a> will list all station information<br/><br/>"
            f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a> will list all observed temperature data for the most active weather station, USC00519281.<br/><br/>"
            f"/api/v1.0/start_date -- You may use your own custom date (YYYY-MM-DD) to observe the min, max, and average temperature between this start date and the most recent date recorded.<br/><br/>"
            f"/api/v1.0/start_date/end_date -- You may use your own custom dates (YYYY-MM-DD) to observe the min, max, and average temperature between these two dates"
    )

##################
# Precipitation
##################
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #Find the most recent date in dataset
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    
    # Calculate the date one year from the last date in data set.
    query_date = dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    """Return a list of all precipitation measurements from the query date"""
    precipitation = session.query(Measurement.date, Measurement.prcp).\
                    filter(Measurement.date >= query_date).all()

    session.close()

    # Create a dictionary from the row data with 'date' as key and 'prcp' as value and append to a list.
    all_precipitation = []
    for date, prcp in precipitation:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)

##################
# Stations
##################
@app.route("/api/v1.0/station")
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of station data"""
    # Query all stations
    results = session.query(Station.id, Station.station, Station.name).all()

    #GOOD PRACTICE TO CLOSE THE SESSION!!
    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_stations = []
    for id, station, name in results:
        station_dict = {}
        station_dict["station_id"] = id
        station_dict["station"] = station
        station_dict["station_name"] = name
        all_stations.append(station_dict)

    return jsonify(all_stations)

##################
# TOBS
##################
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #Find the most recent date in dataset
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    
    # Calculate the date one year from the last date in data set.
    query_date = dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    """Return a list of tobs data for most active station, USC00519281"""
    # Query all tobs
    results = session.query(Measurement.date, Measurement.tobs).\
                    filter(Measurement.station == "USC00519281").\
                    filter(Measurement.date >= query_date).all()

    #GOOD PRACTICE TO CLOSE THE SESSION!!
    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_tobs = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

##################
# Start Date
##################
@app.route("/api/v1.0/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #converts start date string into date format
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date."""
    
    results = session.query(func.min(Measurement.tobs), 
                            func.max(Measurement.tobs), 
                            func.avg(Measurement.tobs)).\
                            filter(Measurement.date >= start_date).all()

    #GOOD PRACTICE TO CLOSE THE SESSION!!
    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    temp_list = []
    for min, max, avg in results:
        temp_dict = {}
        temp_dict["min"] = min
        temp_dict["max"] = max
        temp_dict["avg"] = avg
        temp_list.append(temp_dict)

    return jsonify(temp_list)

######################
# Start and End Dates
######################
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #converts start and end date string into date format
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature between a given start and end date."""
    
    results = session.query(func.min(Measurement.tobs), 
                            func.max(Measurement.tobs), 
                            func.avg(Measurement.tobs)).\
                            filter(Measurement.date >= start_date).\
                            filter(Measurement.date <= end_date).all()

    #GOOD PRACTICE TO CLOSE THE SESSION!!
    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    temp_list = []
    for min, max, avg in results:
        temp_dict = {}
        temp_dict["min"] = min
        temp_dict["max"] = max
        temp_dict["avg"] = avg
        temp_list.append(temp_dict)

    return jsonify(temp_list)

if __name__ == '__main__':
    app.run(debug=True)