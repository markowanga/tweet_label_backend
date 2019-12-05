import datetime
import pymongo
import pandas as pd
import random

mongo_client = pymongo.MongoClient("mongodb://root:password@192.168.0.124:27017/")
labelling_db = mongo_client['tweets_labelling']
abortion_collection = labelling_db['abortion']

ALL_USERS = ['Daniel', 'Dawid', 'Marcin', 'Maciek']


def query_from_tweet_id(tweet_id):
    return {'tweet_id': tweet_id}


def query_from_tweet_id_and_username(tweet_id, username):
    return {'tweet_id': tweet_id, 'username': username}


def get_all_tweets():
    return [it for it in abortion_collection.find()]


def get_all_tweets_by_user(username):
    return [it for it in abortion_collection.find() if it['username'] == username]


def random_index(n):
    return random.randrange(0, n)


def get_random_not_labelled_tweet_by_username(username):
    not_labelled_tweets = [it for it in get_all_tweets() if it['label'] == '' and it['username'] == username]
    items_count = len(not_labelled_tweets)
    return not_labelled_tweets[random_index(items_count)] if items_count > 0 else None


def save_label_for_user(tweet_id, label, username, note):
    new_values = {
        "$set": {
            "label": label,
            'note': note,
            'update_time': datetime.datetime.now()
        }
    }
    abortion_collection.update(query_from_tweet_id_and_username(tweet_id, username), new_values)
    return


def get_labelled_tweets():
    return [it for it in get_all_tweets() if it['label'] != '']


def get_df_with_all():
    df = pd.DataFrame(get_all_tweets())
    df = df.drop(['_id'], axis=1)
    return df


def insert_tweets_for_all_user(tweets):
    get_df_with_all().to_json(datetime.datetime.now().strftime("%m-%d-%Y--%H-%M-%S") + '.json')
    # abortion_collection.delete_many({})
    now = datetime.datetime.now()
    for username in ALL_USERS:
        tweets_to_insert = [
            {
                'tweet_id': it['tweet_id'],
                'tweet_content': it['tweet_content'],
                'hashtags': it['hashtags'],
                'label': it['label'],
                'insert_time': now,
                'update_time': it['update_time'],
                'username': username
            }
            for it in tweets
        ]
        abortion_collection.insert_many(tweets_to_insert)

    return
