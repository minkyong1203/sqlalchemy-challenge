import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import numpy as np

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect db into new model
Base = automap_base()

# reflect tables
Base.prepare(engine, reflect=True)

# save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)

@app.route("/")

def home():
    return(
        """Available routes:
        <br><a href="/api/v1.0/precipitation">Precipitation data</a>
        <br><a href="/api/v1.0/stations">Stations</a>
        <br><a href="/api/v1.0/tobs">Temperature data</a>
        <br><a href="/api/v1.0/<start>">Temperature after start date</a>
        <br><a href="/api/v1.0/<start>/<end>">Temperature for date range</a>
        """
    )


@app.route("/api/v1.0/precipitation")
   
def precipitation():
    # Create session link from Python to DB
    session = Session(engine)
    
    # Convert the query results from your precipitation analysis using date as key, prcp as value
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    last_12mths = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= query_date).all()
    
    session.close()

    # Convert list of dates and precipitation into dictionary
    prcp_dict = {}

    for date, prcp in last_12mths:
        prcp_dict[date]= prcp
        
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")

def stations():
    session = Session(engine)
    station_list = session.query(Measurement.station).all()
    
    session.close()
    
    all_stations = list(np.ravel(station_list))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")

def tobs():
    session = Session(engine)
    
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    temp = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= query_date).all()
    
    session.close()
    
    temp_data = list(np.ravel(temp))
    
    return jsonify(temp_data)

@app.route("/api/v1.0/<start>")

def temp_after(start):
    
    session = Session(engine)
    
    temp_values = []
    
    lowest = session.query(func.min(Measurement.tobs)).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= start).all()
    temp_values.append(lowest)

    highest = session.query(func.max(Measurement.tobs)).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= start).all()
    temp_values.append(highest)

    average = session.query(func.avg(Measurement.tobs)).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= start).all()
    temp_values.append(average)
    
    session.close()
    
    temp_values = list(np.ravel(temp_values))
    
    return(f"From {start}, the lowest, highest, and average temperature were (in that order): {temp_values}")


@app.route("/api/v1.0/<start>/<end>")

def temp_range(start, end):
    session = Session(engine)
    
    temp_values = []
    
    lowest = session.query(func.min(Measurement.tobs)).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= start).\
    filter(Measurement.date <= end).all()
    temp_values.append(lowest)

    highest = session.query(func.max(Measurement.tobs)).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= start).\
    filter(Measurement.date <= end).all()
    temp_values.append(highest)

    average = session.query(func.avg(Measurement.tobs)).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= start).\
    filter(Measurement.date <= end).all()
    temp_values.append(average)
    
    session.close()
    
    temp_values = list(np.ravel(temp_values))
    
    return(f"From {start} to {end}, the lowest, highest, and average temperature were (in that order): {temp_values}")

if __name__ == "__main__":
    app.run(debug=True)
