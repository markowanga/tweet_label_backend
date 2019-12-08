from flask import Flask, request, jsonify, send_file, send_from_directory
import pandas as pd
from flask_cors import CORS, cross_origin
import seaborn as sns
import matplotlib.pyplot as plt
import mongo_user_methods as mmu
import stats_generator

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
    labelling_tag = request.args.get('labelling_tag')
    tweet = mmu.get_random_not_labelled_tweet_by_username(username, labelling_tag)
    return jsonify({
        'id': str(tweet['tweet_id']),
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
    labelling_tag = request_body['labelling_tag']
    mmu.save_label_for_user(tweet_id, label, username, note, labelling_tag)
    return '', 204


@app.route("/send_to_experts", methods=['PUT'])
@cross_origin()
def send_to_experts():
    request_body = request.get_json()
    tweet_id = request_body['tweet_id']
    username = request_body['username']
    labelling_tag = request_body['labelling_tag']
    mmu.mark_as_super_difficult_tweet(tweet_id, username, labelling_tag)
    return '', 204


@app.route("/stats", methods=['GET'])
@cross_origin()
def get_stats():
    username = request.args.get('username')
    labelling_tag = request.args.get('labelling_tag')
    tweets = mmu.get_username_tag_tweets(username, labelling_tag)
    all_tweets_count = len(tweets)
    labelled_tweets_count = len([it for it in tweets if it['label'] != ''])
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
    flights = pd.pivot_table(flights, values='tweet_id', index=['label'], columns=['username'], aggfunc=len)
    fig, ax = plt.subplots(figsize=(12, 3))
    sns.heatmap(flights, annot=True, fmt=".0f")
    fig.savefig('output.png')
    return send_file("output.png", mimetype='image/gif', cache_timeout=0)


@app.route('/get_all_results', methods=['GET'])
def download():
    mmu.get_df_with_all().to_json('results.json')
    return send_from_directory(directory='', filename="results.json")


@app.route('/tweet_labels_file', methods=['GET'])
def download_tweet_labels_file():
    lines = stats_generator.generate_text_with_report_by_tweets(mmu.get_df_with_all().sort_values('insert_time'))
    with open('labels.txt', 'w') as the_file:
        for line in lines:
            the_file.write(line + '\n')
    return send_from_directory(directory='', filename="labels.txt")


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
