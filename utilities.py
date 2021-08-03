import re
import string
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import TweetTokenizer

month_list = ["01-Jan", "02-Feb", "03-Mar", "04-Apr", "05-May", "06-Jun", "07-Jul", "08-Aug", "09-Sep", "10-Oct",
              "11-Nov", "12-Dec"]


def sentiment_line_graph_wrt_month(pos, neg, neut, month_number, graph_dff, keyword=""):
    def plot_graph(x, graph_dfff):
        my_dpi = 200
        color_array = ['blue', 'red', 'grey']
        plt.rcParams['figure.figsize'] = 10, 5
        plt.figure(figsize=(1280 / my_dpi, 720 / my_dpi), dpi=my_dpi)
        for i, keyword_graph in enumerate(graph_dfff.columns):
            plt.plot(x, graph_dfff[keyword_graph], color=color_array[i], linestyle='solid', linewidth=2,
                     marker='o', markerfacecolor=color_array[i], markersize=7)
        plt.xlabel('Month')
        plt.ylabel('Tweet counts')
        plt.title('Sentiment trend over time - ' + keyword)
        plt.legend(graph_dfff.columns)
        plt.savefig("img/sentiment/plot_sentiment_trend_" + keyword + ".png", format="png", dpi=my_dpi)
        plt.show()

    graph_row = list()
    graph_row.append(pos)
    graph_row.append(neg)
    graph_row.append(neut)

    row_series = pd.Series(graph_row, index=graph_dff.columns)
    graph_dff = graph_dff.append(row_series, ignore_index=True)
    # print(graph_dff)

    if month_number == 12:
        print("Plotting line graph for sentiments...")
        # Remove number from month list, to be used as x axis
        x = []
        for monthName in month_list:
            x.append(monthName[3:])

        plot_graph(x, graph_dff)
        print("Done.")

    return graph_dff


def process_tweet(tweet):
    """Process tweet function.
    Input:
        tweet: a string containing a tweet
    Output:
        tweets_clean: a list of words containing the processed tweet
    """
    stemmer = PorterStemmer()
    stopwords_english = stopwords.words('english')
    # remove stock market tickers like $GE
    tweet = re.sub(r'\$\w*', '', tweet)
    # remove old style retweet text "RT"
    tweet = re.sub(r'^RT[\s]+', '', tweet)
    # remove hyperlinks
    tweet = re.sub(r'https?:\/\/.*[\r\n]*', '', tweet)
    # remove hashtags
    # only removing the hash # sign from the word
    tweet = re.sub(r'#', '', tweet)
    # tokenize tweets
    tokenizer = TweetTokenizer(preserve_case=False, strip_handles=True,
                               reduce_len=True)
    tweet_tokens = tokenizer.tokenize(tweet)

    tweets_clean = []
    for word in tweet_tokens:
        if (word not in stopwords_english and  # remove stopwords
                word not in string.punctuation):  # remove punctuation
            # tweets_clean.append(word)
            stem_word = stemmer.stem(word)  # stemming word
            tweets_clean.append(stem_word)

    return tweets_clean


def build_freqs(tweets, ys):
    """Build frequencies.
    Input:
        tweets: a list of tweets
        ys: an m x 1 array with the sentiment label of each tweet
            (either 0 or 1)
    Output:
        freqs: a dictionary mapping each (word, sentiment) pair to its
        frequency
    """
    # Convert np array to list since zip needs an iterable.
    # The squeeze is necessary or the list ends up with one element.
    # Also note that this is just a NOP if ys is already a list.
    yslist = np.squeeze(ys).tolist()

    # Start with an empty dictionary and populate it by looping over all tweets
    # and over all processed words in each tweet.
    freqs = {}
    for y, tweet in zip(yslist, tweets):
        for word in process_tweet(tweet):
            pair = (word, y)
            if pair in freqs:
                freqs[pair] += 1
            else:
                freqs[pair] = 1

    return freqs
