import pandas as pd
from textblob import TextBlob
import matplotlib.pyplot as plt

month_list = ["01-Jan", "02-Feb", "03-Mar", "04-Apr", "05-May", "06-Jun", "07-Jul", "08-Aug", "09-Sep", "10-Oct",
              "11-Nov", "12-Dec"]
month_iterator = 1


def run_all(month_number, graph_dff):

    # Load pickled dataframe

    df_clean = pd.read_pickle("data/pickle-data/" + month_list[month_number - 1] + "-df.pkl")
    data = df_clean

    # Get all the English tweets
    data_en = data

    data_en = data_en.drop(['date', 'likes', 'retweets', 'tweet_id', 'screen_name', 'Unnamed: 0'], axis=1)

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
        plt.title('Sentiment trend over time')
        plt.legend(graph_dfff.columns)
        plt.savefig("img/sentiment/plot_sentiment_trend.png", format="png", dpi=my_dpi)
        plt.show()

    graph_row = list()
    graph_row.append(pos)
    graph_row.append(neg)
    graph_row.append(neut)

    row_series = pd.Series(graph_row, index=graph_dff.columns)
    graph_dff = graph_dff.append(row_series, ignore_index=True)

    if month_number == 12:
        print("Plotting line graph for sentiments...")
        # Remove number from month list, to be used as x axis
        x = []
        for monthName in month_list:
            x.append(monthName[3:])
        print(graph_dff)
        plot_graph(x, graph_dff)
        print("Done.")

    return graph_dff


graph_df = pd.DataFrame(columns=['Positive', 'Negative', 'Neutral'])

for i in range(1, 12 + 1):
    graph_df = run_all(i, graph_df)
