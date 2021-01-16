#Dependencies
import numpy as np
import pandas as pd
import datetime as dt
import pprint
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy import create_engine, inspect, func
from flask import Flask, jsonify

####DATABASE SETUP#####
#Create Engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect database into a new model, and reflect the tables
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station


#####FLASK SETUP######

app = Flask(__name__)
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to Hawaii's Climate Page!"
        f"<br/>"
        f"Available Routes:<br/>"
        f"<br/>"  
        f"Precipitation data with dates:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>" 
        f"List of stations:<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>" 
        f"Most Active station's dates and temps:<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>" 
        f"Min,Avg,and Max Temp for date between dates of(2010-01-01 thru 2017-08-23).Please enter date in yyyy-mm-dd format:"
        f"<br/>" 
        f"/api/v1.0/yyyy-mm-dd"
        f"<br/>"
        f"<br/>"
        f"Min,Avg,and Max Temp for dates between dates of(2010-01-01 thru 2017-08-23).Please enter start & end date in yyyy-mm-dd format:"
        f"<br/>"
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
        )
##Convert the query results to a dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create the session link
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    all_precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict['date'] = date
        precipitation_dict['prcp'] = prcp
        all_precipitation.append(precipitation_dict)
    return jsonify(all_precipitation)    
@app.route("/api/v1.0/stations")
def stations():
    # Create the session link
    session = Session(engine)
    results = session.query(Station.station, Station.name).all()
    session.close()
    all_stations = []
    for station, name in results:
        stations_dict = {}
        stations_dict['station'] = station
        stations_dict['name'] = name
        all_stations.append(stations_dict)
    return jsonify(all_stations)
@app.route("/api/v1.0/tobs")
def tobs():
    # Create the session link
    session = Session(engine)
    most_recent_date= session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    date_last_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    #active_stations=(session.query(Measurement.station,Station.name,func.count(Measurement.id))
    #.filter(Measurement.station == Station.station)
    #.group_by(Measurement.station)
    #.order_by(func.count(Measurement.id).desc()).first()
   # .all()) 
    results = session.query(Measurement.station,Measurement.date,  Measurement.tobs).\
                filter(Measurement.date >= '2016-08-23').\
                filter(Measurement.station=='USC00519281').\
                order_by(Measurement.date).all()
    session.close()
    all_tobs = []
    for station, date, tobs in results:
        tobs_dict = {}
        tobs_dict['station']= station
        tobs_dict['date'] = date
        tobs_dict['tobs'] = tobs
        all_tobs.append(tobs_dict)
    return jsonify(all_tobs)
@app.route('/api/v1.0/<start>')
def start(start):
    session = Session(engine)
    results = session.query(Measurement.date,func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        group_by(Measurement.date).all()
    session.close()

    start_tob = []
    for date,min,avg,max in results:
        start_tobs_dict = {}
        
        start_tobs_dict["Date"] = date
        start_tobs_dict["Min"] = min
        start_tobs_dict["Average"] = avg
        start_tobs_dict["Max"] = max
        start_tob.append(start_tobs_dict)
        if start == date:
         return jsonify(start_tob)
   
        return jsonify({"error": f'Date not found: {start}'}), 404  

@app.route('/api/v1.0/<start>/<stop>')
def start_stop(start,stop):
    session = Session(engine)
    results = session.query(Measurement.date,func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= stop).\
        group_by(Measurement.date).all()
    session.close()

    start_stop_tob = []
    for date,min,avg,max in results:
        start_stop_tobs_dict = {}
        
        start_stop_tobs_dict["Date"] = date
        start_stop_tobs_dict["Min"] = min
        start_stop_tobs_dict["Average"] = avg
        start_stop_tobs_dict["Max"] = max
        start_stop_tob.append(start_stop_tobs_dict)
        #if date == start and date == stop:
    return jsonify(start_stop_tob)
        #return jsonify({"error": f'Date not found: {start,stop}'}), 404
    
if __name__ == "__main__":
    app.run(debug=True)