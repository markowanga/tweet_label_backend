from flask import Flask, request, jsonify, send_file
import pandas as pd
from random import shuffle
from flask_cors import CORS, cross_origin
import datetime
import seaborn as sns
import matplotlib.pyplot as plt

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app)

TWEETS_FILE = "data/data.json"


def read_all_tweets():
    return pd.read_json(TWEETS_FILE)


def update_all_tweets(df):
    df.to_json(TWEETS_FILE)


def group_by_counts(df):
    values = list(df['label'].to_numpy().T)
    unique = set(values)
    dic = {}
    for it in unique:
        dic[it] = values.count(it)
    return dic


@app.route("/get_unlabelled_tweet", methods=['GET'])
@cross_origin()
def get_unlabelled_tweet():
    tweets = read_all_tweets()
    arr = [(it[0], it[1]) for it in tweets[tweets.label == ''].to_numpy()]
    shuffle(arr)
    return jsonify({
        'id': arr[0][0],
        'tweet': arr[0][1]
    })


@app.route("/save_label", methods=['PUT'])
@cross_origin()
def save_label():
    request_body = request.get_json()
    tweet_id = request_body['tweet_id']
    label = request_body['label']
    username = request_body['username']
    note = request_body['note']
    tweets = read_all_tweets()
    tweets.loc[tweets.tweet_id == tweet_id, 'label'] = label
    tweets.loc[tweets.tweet_id == tweet_id, 'username'] = username
    tweets.loc[tweets.tweet_id == tweet_id, 'note'] = note
    tweets.loc[tweets.tweet_id == tweet_id, 'update_time'] = datetime.datetime.now()
    update_all_tweets(tweets)
    return '', 204


@app.route("/stats", methods=['GET'])
@cross_origin()
def get_stats():
    tweets = read_all_tweets()
    all_tweets_count = tweets.shape[0]
    labelled_tweets_count = tweets[tweets.apply(lambda x: x.label != '', axis=1)].shape[0]
    return jsonify({
        'all_tweets_count': all_tweets_count,
        'labelled_tweets_count': labelled_tweets_count
    })


@app.route("/stats_detailed", methods=['GET'])
@cross_origin()
def get_stats_detailed():
    tweets = read_all_tweets()
    return jsonify(group_by_counts(tweets))


@app.route("/labelled_tweets", methods=['GET'])
@cross_origin()
def get_labelled_tweets():
    tweets = read_all_tweets()
    tweets = tweets[tweets.label != ''].sort_values(by=['update_time'], ascending=False)
    list_to_return = []
    for index, row in tweets.iterrows():
        d = row.to_dict()
        d['update_time'] = d['update_time'].isoformat()
        list_to_return.append(d)
    return jsonify({'tweets': list_to_return})


@app.route('/stats_heatmap')
def get_stats_heatmap():
    flights = read_all_tweets()
    flights = pd.pivot_table(flights, values='tweet_id', index=['label'],  columns=['username'], aggfunc=len)
    fig, ax = plt.subplots(figsize=(12, 3))
    sns.heatmap(flights, annot=True, fmt=".0f")
    fig.savefig('output.png')
    return send_file("output.png", mimetype='image/gif', cache_timeout=0)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
