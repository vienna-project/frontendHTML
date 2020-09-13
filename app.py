import json
from random import sample 
from dateutil.parser import parse

from flask import Flask, render_template


def date_parser(date):
    tzinfos = {"UTC": 0}
    date = parse(date, tzinfos=tzinfos)
    return date.strftime("%Y.%m")


def rec_receiver():
    with open('./result.json') as f:
        data = json.load(f)
    recs = sample(data, 3)
    return recs


def meta_filter(rec):
    filtered_rec = {}
    
    # identifier
    filtered_rec['owner'] = rec['owner']
    filtered_rec['name'] = rec['name']
    filtered_rec['image'] = rec['openGraphImageUrl']
    
    # time-related
    filtered_rec['from'] = date_parser(rec['createdAt'])
    filtered_rec['to'] = date_parser(rec['updatedAt'])
    
    # popularity
    
    return filtered_rec
    


app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    recs = rec_receiver()
    recs = [meta_filter(rec) for rec in recs]
    
    return render_template(
                'search_result.html',
                recs=recs)

@app.route('/info')
def info():
    return render_template('search_result.html')

app.run(debug = True, port=8078)