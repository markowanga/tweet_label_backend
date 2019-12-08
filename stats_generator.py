import pandas as pd


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
