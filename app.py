import json
from random import sample 
from dateutil.parser import parse

from elasticsearch import Elasticsearch
from flask import Flask, render_template, request
from flask import jsonify


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
    
    # meta
    filtered_rec['language'] = rec['languages']
    if filtered_rec['language']:
        filtered_rec['language'] = ", ".join(rec['languages'][:3])
    
    filtered_rec['topics'] = ", ".join(rec['repositoryTopics'][:3])
    if filtered_rec['topics']:
        filtered_rec['topics'] = ", ".join(filtered_rec['topics'][:3])

    filtered_rec['description'] = rec['description']
    if filtered_rec['description']: 
        filtered_rec['description'] = filtered_rec['description'][:200]
    
    return filtered_rec


app = Flask(__name__)


@app.route('/')
def index():
    recs = rec_receiver()
    recs = [meta_filter(rec) for rec in recs]
    
    return render_template(
                'search_result.html',
                recs=recs)


@app.route("/autocomplete", methods=["GET"])
def autocomplete():
    query = request.args.get("q", "tensor")
    docs = Elasticsearch().search(body={
        "query": {
            "multi_match": {
                "query": query,
                "type": "bool_prefix",
                "fields": [
                    "name"
                ]
            }
        },
        "sort": [
            {"stargazers": {"order": "desc"}}
        ],
        "from": 0,
        "size": 10

    })

    res = [ doc["_source"]["owner"] + "/" + doc["_source"]["name"] for doc in
            docs['hits']['hits']]

    return jsonify(res)


if __name__ == "__main__":
    app.run(debug=True, port=8078)