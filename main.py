from flask import Flask, request
import pandas as pd
from random import shuffle
from flask_cors import CORS, cross_origin
import json
import datetime

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app)

TWEETS_FILE = "data/data.json"


def read_all_tweets():
    return pd.read_json(TWEETS_FILE)


def update_all_tweets(df):
    df.to_json(TWEETS_FILE)


def get_df_id_by_tweet_id(df, tweet_id):
    return df[df['tweet_id'] == tweet_id].index.tolist()[0]


def group_by_counts(df):
    values = list(df['label'].to_numpy().T)
    unique = set(values)
    dic = {}
    for it in unique:
        dic[it] = values.count(it)
    return dic


@app.route("/get_unlabelled_tweet")
@cross_origin()
def get_unlabelled_tweet():
    tweets = read_all_tweets()
    print(tweets.iloc(0))
    arr = [(it[0], it[1]) for it in tweets[tweets.label == ''].to_numpy()]
    shuffle(arr)
    return json.dumps({
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
    row_id = get_df_id_by_tweet_id(tweets, tweet_id)
    tweets.xs(row_id)['label'] = label
    tweets.xs(row_id)['username'] = username
    tweets.xs(row_id)['note'] = note
    tweets.xs(row_id)['update_time'] = datetime.datetime.now()
    print(tweets.iloc(row_id))
    update_all_tweets(tweets)
    return '', 204


@app.route("/stats")
@cross_origin()
def get_stats():
    tweets = read_all_tweets()
    all_tweets_count = tweets.shape[0]
    labelled_tweets_count = tweets[tweets.apply(lambda x: x.label != '', axis=1)].shape[0]
    return json.dumps({
        'all_tweets_count': all_tweets_count,
        'labelled_tweets_count': labelled_tweets_count
    })


@app.route("/stats_detailed")
@cross_origin()
def get_stats_detailed():
    tweets = read_all_tweets()
    return json.dumps(group_by_counts(tweets))


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
