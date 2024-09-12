import os
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.sql import func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import sqlite3

Base = automap_base()

# engine, suppose it has two tables 'user' and 'address' set up
engine = create_engine("sqlite:///bincomphptest.db")

# reflect the tables
Base.prepare(engine, reflect=True)

# mapped classes are now created with names by default
# matching that of the table name.
PollingUnit = Base.classes.polling_unit
Ward = Base.classes.ward
LGA = Base.classes.lga
AnnouncedPuResults = Base.classes.announced_pu_results
AnnouncedLgaResults = Base.classes.announced_lga_results
Party = Base.classes.party


session = Session(engine)
session.commit()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bincomphptest.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route('/')
def index():
    return 1

@app.route('/polling_units/<int:id>')
def polling_unit(id):
    result = get_polling_unit(id)
    return render_template('polling_unit.html', result=result)


@app.route('/total_lga/<int:lga_id>')
def total_lga(lga_id):
    polling_unit = session.query(PollingUnit).filter_by(lga_id=lga_id).all()
    polling_units = [[i.partyname, 0] for i in session.query(Party).all()]
    total = 0
    for res in polling_unit:
        polling_unit_id = res.polling_unit_id
        print( polling_unit_id)
        polling_unit_result = get_polling_unit(polling_unit_id)
        print(polling_units)
        
        i = 0
        for item in polling_unit_result:
            if item[0] == polling_units[i][0]:
                polling_units[i][1] += item[1]
                total += item[1]
                i += 1

    print(total)
    response = {
        "polling_units": polling_units,
        "total": total
    }
    return render_template('total_lga.html', response=response)


def get_polling_unit(id):
    announced_pu_results = session.query(AnnouncedPuResults).filter_by(polling_unit_uniqueid=id).all()
    result = []
    for res in announced_pu_results:
        party, score = res.party_abbreviation, res.party_score
        result.append([
            party,
            score
        ])
    return result


if __name__ == '__main__':
    app.run(debug=True)
