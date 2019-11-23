from flask import Flask, request
import pandas as pd
from random import shuffle
from flask_cors import CORS, cross_origin
import json

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

TWEETS_FILE = "data/data.json"


def read_all_tweets():
    return pd.read_json(TWEETS_FILE)


def update_all_tweets(df):
    df.to_json(TWEETS_FILE)
    pass


def get_df_id_by_tweet_id(df, tweet_id):
    return df[df['tweet_id'] == tweet_id].index.tolist()[0]


@app.route("/get_unlabelled_tweet")
@cross_origin()
def get_unlabelled_tweet():
    tweets = read_all_tweets()
    arr = [(it[0], it[1]) for it in tweets[tweets.label == 'NONE'].to_numpy()]
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
    tweets = read_all_tweets()
    row_id = get_df_id_by_tweet_id(tweets, tweet_id)
    tweets.xs(row_id)['label'] = label
    update_all_tweets(tweets)
    return '{}'


@app.route("/stats")
@cross_origin()
def save_label():
    tweets = read_all_tweets()
    all_tweets_count = tweets.shape[0]
    labelled_tweets_count = tweets[tweets.apply(lambda x: x.label != 'NONE', axis=1)].shape[0]
    return json.dumps({
        'all_tweets_count': all_tweets_count,
        'labelled_tweets_count': labelled_tweets_count
    })


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
