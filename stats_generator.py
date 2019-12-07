import pandas as pd
from statsmodels.stats.inter_rater import fleiss_kappa


def generate_text_with_report_by_tweets(tweets_label_df: pd.DataFrame):
    final_string_list = []

    def add_line(line):
        final_string_list.append(line)

    filtered = tweets_label_df.sort_values('insert_time').tail(400)

    tweet_id_list = list(set(list(filtered.sort_values('insert_time', ascending=True).tail(400)['tweet_id'].to_numpy())))
    for tweet_id_index in range(len(tweet_id_list)):
        tweet_id = tweet_id_list[tweet_id_index]
        selected_tweets = filtered[filtered['tweet_id'] == tweet_id]
        add_line('--------------------')
        add_line('')
        add_line('#' + str(tweet_id_index + 1))
        add_line('tweet_id: ' + tweet_id)
        add_line('inserted_time: ' + str(selected_tweets['insert_time'].to_numpy()[0]))
        add_line('')
        add_line('tweet_content: ')
        add_line(selected_tweets['tweet_content'].to_numpy()[0])
        add_line('')

        for index, values in selected_tweets.iterrows():
            add_line('label -> ' + values['username'] + ': ' + values['label'])

        add_line('')
        add_line('--------------------')

    return final_string_list


def get_fleiss_kappa_metric(tweets_label_df: pd.DataFrame):
    tweet_id_list = list(set(tweets_label_df['tweet_id'].to_numpy()))
    username_list = list(set(tweets_label_df['username'].to_numpy()))
    labels_list = [[] for _ in username_list]
    print(len(tweet_id_list))
    print(labels_list)
    for tweet_id in tweet_id_list:
        filtered_data = tweets_label_df[tweets_label_df['tweet_id'] == tweet_id]
        for username_index in range(len(username_list)):
            username = username_list[username_index]
            label = filtered_data[tweets_label_df['username'] == username]['label'].to_numpy()[0]
            labels_list[username_index].append(label)
    fleiss_kappa(labels_list)
