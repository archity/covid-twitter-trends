import pickle
import string
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt

nltk.download('stopwords')

month_list = ["01-Jan", "02-Feb", "03-Mar", "04-Apr", "05-May", "06-Jun", "07-Jul", "08-Aug", "09-Sep", "10-Oct",
              "11-Nov", "12-Dec"]

month_iterator = 1


def run_all(month_number, graph_dff):
    table_df = pd.read_csv('data/' + month_list[month_number - 1] + '-Tweets.csv')

    # Loop through the whole list and remove the coloumn headings,
    # since they repeat after every 100 entries

    for i in range(len(table_df)):
        if table_df.loc[i, "tweet"] == "tweet":
            table_df = table_df.drop(index=i)

    # ------------------------------------------------------------------------------
    df_clean = table_df

    # Function for removing @ mentions and hyperlinks
    def remove_mentions(text):
        # newtext = re.sub('@.*? ', '', text)
        newtext = re.sub(r'https?:\/\/.*[\r\n]*', '', text)
        return newtext

    df_clean['tweet'] = table_df.tweet.apply(lambda x: remove_mentions(x))

    # Save the dataframe for future use
    df_clean.to_pickle("./data/pickle-data/" + month_list[month_number - 1] + "-df.pkl")

    # ------------------------------------------------------------------------------
    # Convert all the letters of words to lowercase
    df_clean['tweet'] = df_clean['tweet'].str.lower()

    # Special replacement for 'í' (coronavírus)
    df_clean['tweet'] = df_clean['tweet'].str.replace('í', 'i')

    # ------------------------------------------------------------------------------

    # Remove stopwords

    stopwords_english = stopwords.words('english')
    stopwords_french = stopwords.words('french')
    stopwords_spanish = stopwords.words('spanish')

    lang_stopwords = stopwords_english + stopwords_french + stopwords_spanish

    lang_pat = r'\b(?:{})\b'.format('|'.join(lang_stopwords))

    df_clean.loc[:, 'tweet'] = df_clean.loc[:, 'tweet'].str.replace(lang_pat, '')
    # ------------------------------------------------------------------------------

    # Custom single letter words
    custom_stop_letters = ['é', 'ê', 'è', 'î']
    cust_pat = r'\b(?:{})\b'.format('|'.join(custom_stop_letters))
    df_clean.loc[:, 'tweet'] = df_clean.loc[:, 'tweet'].str.replace(cust_pat, '')

    # Remove single letter words
    single_letter_words = list(string.ascii_letters)
    letter_pat = r'\b(?:{})\b'.format('|'.join(single_letter_words))
    df_clean.loc[:, 'tweet'] = df_clean.loc[:, 'tweet'].str.replace(letter_pat, '')

    # ------------------------------------------------------------------------------

    # Remove punctuation marks from every tweet
    punc_chars = '''!()-[]{};:'"\,<>./?@#$%^&*_~’‘´`~|+'''
    df_clean.loc[:, 'tweet'] = df_clean.loc[:, 'tweet'].str.translate(str.maketrans('', '', punc_chars))

    # ------------------------------------------------------------------------------

    # Go through each tweet and put individual word into a list

    word_list = []

    for tweet in df_clean.tweet:
        word_list += (tweet.split())

    # Get the count values of all the words
    words_counter = Counter(word_list).most_common()

    # Convert the Counter list to a Pandas dataframe
    words_counter_df = pd.DataFrame.from_records(list(dict(words_counter).items()), columns=['word', 'count'])

    with open('all-words.txt', 'w', encoding="utf-8") as filehandle:
        for listitem in word_list:
            filehandle.write('%s\n' % listitem)

    # ------------------------------------------------------------------------------

    # Now we remove words like covid, coronavirus
    covid_words = ["covid", "coronavirus", "covid-19", "covid19"]
    for covword in covid_words:
        words_counter_df.drop(words_counter_df[words_counter_df.word == covword].index, inplace=True)

    # Remove "&amp;". It occurs several times ('&' and ';' have already been removed)
    words_counter_df.drop(words_counter_df[words_counter_df.word == "amp"].index, inplace=True)

    words_counter_df = words_counter_df.reset_index(drop=True)

    top_word_list = []

    for word in words_counter_df['word'][:20]:
        top_word_list += (word.split())

    with open('top20-words-' + month_list[month_number - 1] + '.txt', 'w', encoding="utf-8") as filehandle:
        for listitem in top_word_list:
            filehandle.write('%s\n' % listitem)

    # Rename the column 'count' to 'freq'
    words_counter_df.columns = ['word', 'freq']

    # Convert pd dataframe to dictionary for input for wordcould
    wordcount_dict = dict(zip(words_counter_df.word, words_counter_df.freq))

    # ------------------------------------------------------------------------------
    # Generate data for line graph for specific keyword

    # Function for plotting the dataframe wrt months
    def plot_graph(x, graph_dfff):
        my_dpi = 200
        plt.rcParams['figure.figsize'] = 10, 5
        for keyword_graph in graph_dfff.columns:
            plt.figure(figsize=(1280 / my_dpi, 720 / my_dpi), dpi=my_dpi)
            plt.plot(x, graph_dfff[keyword_graph], color='blue', linestyle='solid', linewidth=2,
                     marker='o', markerfacecolor='blue', markersize=7)

            plt.xlabel('Month')
            plt.ylabel('Tweet mentions')
            plt.title('Trend of word "' + keyword_graph + '" over time')
            plt.savefig("img/plot_" + keyword_graph + ".png", format="png", dpi=my_dpi)
            plt.show()

    graph_row = list()

    # Get the count of all the keywords for the current month
    for keyword_graph in graph_dff.columns:
        var = words_counter_df[words_counter_df['word'].str.contains(keyword_graph)]['freq']
        graph_row.append(var.sum())

    # Put the counts for current month in a pandas series and add it to the DF
    row_series = pd.Series(graph_row, index=graph_dff.columns)
    graph_dff = graph_dff.append(row_series, ignore_index=True)
    if month_number == 12:
        # Remove number from month list, to be used as x axis
        x = []
        for monthName in month_list:
            x.append(monthName[3:])
        print(graph_dff)
        plot_graph(x, graph_dff)
    """
    # Write plot data to file
    f = open(keyword_graph + "-stats.txt", "a+")
    f.write(str(var.sum()) + "\t")
    f.close()
    """
    # ------------------------------------------------------------------------------

    # Wordcloud

    wc = WordCloud(width=2000, height=1000).generate_from_frequencies(wordcount_dict)
    fig = plt.figure(figsize=(20, 10))
    fig.suptitle(month_list[month_number - 1][3:6] + '. wordcloud', fontsize=20)
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout(pad=1)
    # wc.to_file("img/wordcloud_" + month_list[month_number - 1] + ".png")
    plt.savefig("img/wordcloud_" + month_list[month_number - 1] + ".png", format="png", dpi=100)
    # plt.show()
    print(month_list[month_number - 1][3:] + " done")
    return graph_dff


graph_df = pd.DataFrame(columns=['trump', 'china', 'vaccine', 'mask', 'lockdown'])

for i in range(1, 12 + 1):
    graph_df = run_all(i, graph_df)
