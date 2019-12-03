from flask import Flask, request, jsonify, send_file, send_from_directory
import pandas as pd
from flask_cors import CORS, cross_origin
import seaborn as sns
import matplotlib.pyplot as plt
import mongo_user_methods as mmu

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app)


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
    username = request.args.get('username')
    tweet = mmu.get_random_not_labelled_tweet_by_username(username)
    return jsonify({
        'id': tweet['tweet_id'],
        'tweet': tweet['tweet_content']
    })


@app.route("/save_label", methods=['PUT'])
@cross_origin()
def save_label():
    request_body = request.get_json()
    tweet_id = request_body['tweet_id']
    label = request_body['label']
    username = request_body['username']
    note = request_body['note']
    mmu.save_label_for_user(tweet_id, label, username, note)
    return '', 204


@app.route("/stats", methods=['GET'])
@cross_origin()
def get_stats():
    tweets = mmu.get_df_with_all()
    all_tweets_count = tweets.shape[0]
    labelled_tweets_count = tweets[tweets.apply(lambda x: x.label != '', axis=1)].shape[0]
    return jsonify({
        'all_tweets_count': all_tweets_count,
        'labelled_tweets_count': labelled_tweets_count
    })


@app.route("/stats_detailed", methods=['GET'])
@cross_origin()
def get_stats_detailed():
    tweets = mmu.get_df_with_all()
    return jsonify(group_by_counts(tweets))


@app.route("/labelled_tweets", methods=['GET'])
@cross_origin()
def get_labelled_tweets():
    tweets = mmu.get_df_with_all()
    tweets = tweets[tweets.label != ''].sort_values(by=['update_time'], ascending=False)
    list_to_return = []
    for index, row in tweets.iterrows():
        d = row.to_dict()
        d['update_time'] = d['update_time'].isoformat()
        d['note'] = ''
        d['tweet'] = d['tweet_content']
        d.pop('_id', None)
        d.pop('tweet_content', None)
        list_to_return.append(d)
    return jsonify({'tweets': list_to_return})


@app.route('/stats_heatmap')
@cross_origin()
def get_stats_heatmap():
    flights = mmu.get_df_with_all()
    flights = pd.pivot_table(flights, values='tweet_id', index=['label'],  columns=['username'], aggfunc=len)
    fig, ax = plt.subplots(figsize=(12, 3))
    sns.heatmap(flights, annot=True, fmt=".0f")
    fig.savefig('output.png')
    return send_file("output.png", mimetype='image/gif', cache_timeout=0)


@app.route('/get_all_results', methods=['GET'])
def download():
    mmu.get_df_with_all().to_json('results.json')
    return send_from_directory(directory='', filename="results.json")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
