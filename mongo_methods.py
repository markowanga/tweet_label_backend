import datetime
import pymongo
import pandas as pd
import random

mongo_client = pymongo.MongoClient("mongodb://root:password@192.168.0.124:27017/")
labelling_db = mongo_client['tweets_labelling']
abortion_collection = labelling_db['abortion']


def query_from_tweet_id(tweet_id):
    return {'tweet_id': tweet_id}


def get_all_tweets():
    return [it for it in abortion_collection.find()]


def get_tweet_by_id(tweet_id):
    result_list = [it for it in abortion_collection.find(query_from_tweet_id(tweet_id))]
    return result_list[0] if len(result_list) == 1 else None


def random_index(n):
    return random.randrange(0, n)


def get_random_not_labelled_tweet():
    not_labelled_tweets = [it for it in get_all_tweets() if it['label'] == '']
    items_count = len(not_labelled_tweets)
    return not_labelled_tweets[random_index(items_count)] if items_count > 0 else None


def save_label(tweet_id, label, username, note):
    new_values = {
        "$set": {
            "label": label,
            'username': username,
            'note': note,
            'update_time': datetime.datetime.now()
        }
    }
    abortion_collection.update_one(query_from_tweet_id(tweet_id), new_values)
    return


def get_labelled_tweets():
    return [it for it in get_all_tweets() if it['label'] != '']


def get_df_with_all():
    return pd.DataFrame(get_all_tweets())


def insert_all_tweets(tweets):
    tweets_to_insert = [
        {
            'tweet_id': it['tweet_id'],
            'tweet_content': it['tweet_content'],
            'hashtags': it['hashtags'],
            'label': it['label'],
            'username': it['username'],
            'insert_time': datetime.datetime.now(),
            'update_time': it['update_time']
        }
        for it in tweets
    ]
    abortion_collection.insert_many(tweets_to_insert)
    return
