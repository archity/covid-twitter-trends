import pandas as pd
from textblob import TextBlob
import matplotlib.pyplot as plt

import nltk
from nltk.corpus import twitter_samples
import numpy as np

from utilities import process_tweet, build_freqs, month_list, sentiment_line_graph_wrt_month

month_iterator = 1


def textblob(graph_dff):
    for month_number in range(1, 12 + 1):

        # Load pickled dataframe
        df_clean = pd.read_pickle("data/pickle-data/" + month_list[month_number - 1] + "-df.pkl")

        data_en = df_clean.drop(['date', 'likes', 'retweets', 'tweet_id', 'screen_name', 'Unnamed: 0'], axis=1)

        pol = lambda x: TextBlob(x).sentiment.polarity
        sub = lambda x: TextBlob(x).sentiment.subjectivity

        data_en['polarity'] = data_en['tweet'].apply(pol)
        data_en['subjectivity'] = data_en['tweet'].apply(sub)

        data_en.head(10)

        # ------------------------------------------------------------------------------
        # Scatter plot for sentiment analysis

        plt.rcParams['figure.figsize'] = [10, 8]

        x = data_en.polarity
        y = data_en.subjectivity
        plt.scatter(x, y, color='blue')
        # plt.xlim(-.01, .12)

        plt.title('Sentiment Analysis', fontsize=20)
        plt.xlabel('<-- Negative  ----------------  Positive -->', fontsize=10)
        plt.ylabel('<-- Facts  ----------------  Opinions -->', fontsize=10)
        plt.savefig("img/sentiment/sa-" + month_list[month_number - 1] + ".png", format="png", dpi=200)
        plt.show()

        # ------------------------------------------------------------------------------
        # Plot a pie-chart

        pos = data_en[data_en['polarity'] > 0].shape[0]
        neg = data_en[data_en['polarity'] < 0].shape[0]
        neut = data_en[data_en['polarity'] == 0].shape[0]

        pie_data = [pos, neg, neut]

        my_labels = 'Positive', 'Negative', 'Neutral'
        plt.pie(pie_data, labels=my_labels, autopct='%1.1f%%')
        plt.title('My Tasks')
        plt.axis('equal')
        plt.savefig("img/sentiment/pie-" + month_list[month_number - 1] + ".png", format="png", dpi=200)
        plt.show()
        print(month_list[month_number - 1][3:] + " done")

        # ------------------------------------------------------------------------------

        graph_dff = sentiment_line_graph_wrt_month(pos, neg, neut, month_number, graph_dff, keyword="textblob")

    return graph_dff


def logistic_regression(graph_dff):
    """
    Logistic Regression model trained NLTK's twitter sample tweets
    Code snippets taken and modified from the assignment part of
    course "Natural Language Processing with Classification and Vector Spaces"
    taken from Coursera.

    :return: none
    """

    # Import tweets from NLTK's twitter_sample
    positive_tweets = twitter_samples.strings('positive_tweets.json')
    negative_tweets = twitter_samples.strings('negative_tweets.json')

    # Split data into training and testing sets
    # pos_train, pos_test, neg_train, neg_test = train_test_split(positive_tweets, negative_tweets, 0.2)
    pos_test = positive_tweets[4000:]
    pos_train = positive_tweets[:4000]
    neg_test = negative_tweets[4000:]
    neg_train = negative_tweets[:4000]

    train_x = pos_train + neg_train
    test_x = pos_test + neg_test

    # all_train = np.append(np.ones(len(pos_train), 1), np.zeros(len(neg_train), 1), axis=0)
    # all_test = np.append(np.ones(len(pos_test), 1), np.zeros(len(neg_test), 1), axis=0)

    # Create a numpy array of positive and negative labels.
    # combine positive and negative labels
    train_y = np.append(np.ones((len(pos_train), 1)), np.zeros((len(neg_train), 1)), axis=0)
    test_y = np.append(np.ones((len(pos_test), 1)), np.zeros((len(neg_test), 1)), axis=0)

    # Print the shape train and test sets
    print("train_y.shape = " + str(train_y.shape))
    print("test_y.shape = " + str(test_y.shape))

    # create frequency dictionary
    freqs = build_freqs(train_x, train_y)

    # check the output
    print("type(freqs) = " + str(type(freqs)))
    print("len(freqs) = " + str(len(freqs.keys())))

    # test the function below
    print('This is an example of a positive tweet: \n', train_x[0])
    print('\nThis is an example of the processed version of the tweet: \n', process_tweet(train_x[0]))

    def sigmoid(z):
        """
        Input:
            z: is the input (can be a scalar or an array)
        Output:
            h: the sigmoid of z
        """

        # calculate the sigmoid of z
        h = 1 / (1 + np.exp(-z))

        return h

    def gradient_descent(x, y, theta, alpha, num_iters):
        """
        Input:
            x: matrix of features which is (m,n+1)
            y: corresponding labels of the input matrix x, dimensions (m,1)
            theta: weight vector of dimension (n+1,1)
            alpha: learning rate
            num_iters: number of iterations you want to train your model for
        Output:
            J: the final cost
            theta: your final weight vector
        Hint: you might want to print the cost to make sure that it is going down.
        """

        # get 'm', the number of rows in matrix x
        m = x.shape[0]

        for i in range(0, num_iters):
            # get z, the dot product of x and theta
            z = np.dot(x, theta)

            # get the sigmoid of z
            h = sigmoid(z)

            # calculate the cost function
            J = -1. / m * (np.dot(y.transpose(), np.log(h)) + np.dot((1 - y).transpose(), np.log(1 - h)))

            # update the weights theta
            theta = theta = theta - (alpha / m) * np.dot(x.transpose(), (h - y))

        J = float(J)
        return J, theta

    def extract_features(tweet, freqs):
        """
        Input:
            tweet: a list of words for one tweet
            freqs: a dictionary corresponding to the frequencies of each tuple (word, label)
        Output:
            x: a feature vector of dimension (1,3)
        """
        # process_tweet tokenizes, stems, and removes stopwords
        word_l = process_tweet(tweet)

        # 3 elements in the form of a 1 x 3 vector
        x = np.zeros((1, 3))

        # bias term is set to 1
        x[0, 0] = 1

        # loop through each word in the list of words
        for word in word_l:
            # increment the word count for the positive label 1
            x[0, 1] += freqs.get((word, 1.0), 0)

            # increment the word count for the negative label 0
            x[0, 2] += freqs.get((word, 0.0), 0)

        assert (x.shape == (1, 3))
        return x

    # ------------------------------------------------

    # Training the Logistic Regression model

    # collect the features 'x' and stack them into a matrix 'X'
    X = np.zeros((len(train_x), 3))
    for i in range(len(train_x)):
        X[i, :] = extract_features(train_x[i], freqs)

    # training labels corresponding to X
    Y = train_y

    # Apply gradient descent
    J, theta = gradient_descent(X, Y, np.zeros((3, 1)), 1e-9, 1500)
    print(f"The cost after training is {J:.8f}.")
    print(f"The resulting vector of weights is {[round(t, 8) for t in np.squeeze(theta)]}")

    def predict_tweet(tweet, freqs, theta):
        """
        Input:
            tweet: a string
            freqs: a dictionary corresponding to the frequencies of each tuple (word, label)
            theta: (3,1) vector of weights
        Output:
            y_pred: the probability of a tweet being positive or negative
        """

        # extract the features of the tweet and store it into x
        x = extract_features(tweet, freqs)

        # make the prediction using x and theta
        y_pred = sigmoid(np.dot(x, theta))

        return y_pred

    def test_logistic_regression(test_x, test_y, freqs, theta):
        """
        Input:
            test_x: a list of tweets
            test_y: (m, 1) vector with the corresponding labels for the list of tweets
            freqs: a dictionary with the frequency of each pair (or tuple)
            theta: weight vector of dimension (3, 1)
        Output:
            accuracy: (# of tweets classified correctly) / (total # of tweets)
        """

        # the list for storing predictions
        y_hat = []

        for tweet in test_x:
            # get the label prediction for the tweet
            y_pred = predict_tweet(tweet, freqs, theta)

            if y_pred > 0.5:
                # append 1.0 to the list
                y_hat.append(1)
            else:
                # append 0 to the list
                y_hat.append(0)

        # With the above implementation, y_hat is a list, but test_y is (m,1) array
        # convert both to one-dimensional arrays in order to compare them using the '==' operator
        accuracy = (y_hat == np.squeeze(test_y)).sum() / len(test_x)

        return accuracy

    tmp_accuracy = test_logistic_regression(test_x, test_y, freqs, theta)
    print(f"Logistic regression model's accuracy = {tmp_accuracy:.4f}")

    for month_number in range(1, 12 + 1):
        df_clean = pd.read_pickle("data/pickle-data/" + month_list[month_number - 1] + "-df.pkl")

        data = df_clean.drop(['date', 'likes', 'retweets', 'tweet_id', 'screen_name', 'Unnamed: 0'], axis=1)

        pol = lambda x: predict_tweet(x, freqs, theta)
        data['polarity'] = data['tweet'].apply(pol)

        pos = data[data['polarity'] > 0.5].shape[0]
        neg = data[data['polarity'] < 0.5].shape[0]
        neut = data[data['polarity'] == 0.5].shape[0]

        graph_dff = sentiment_line_graph_wrt_month(pos, neg, neut, month_number, graph_dff, keyword="LogisticRegression")
        print(month_list[month_number - 1][3:] + " done")


if __name__ == '__main__':
    graph_df = pd.DataFrame(columns=['Positive', 'Negative', 'Neutral'])

    # Textblob sentiment analysis
    textblob(graph_df)

    # Logistic regression sentiment analysis
    logistic_regression(graph_df)
