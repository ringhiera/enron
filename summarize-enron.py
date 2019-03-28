import collections
import itertools
import sys
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
from absl import app

TOP_SENDERS = 5


def print_instructions():
    '''prints instructionson stdin'''
    print("Usage: python summarize-enron.py <input file> \nE.g.: python summarize-enron.py enron-event-history-all.csv")


def dateparser(time_in_msecs):
    '''
    converst unix timestamp to datetime
    :param time_in_msecs: Input unix timestamp
    :return: same instant as datetime
    '''
    return datetime.fromtimestamp(float(time_in_msecs) / 1000)


def get_summaries(df):
    '''
    Given the enron dataframe returns the summary statistics (as defined below)

    The Enron event history (.csv, adapted from the widely-used publicly available data set) is attached to this email.
    The columns contain:
        time - time is Unix time (in milliseconds)
        message identifier
        sender
        recipients - pipe-separated list of email recipients
        topic - always empty
        mode - always "email"

    Summary statistics:
    A dataframe with three columns
    "person", "sent", "received"
    where the final two columns contain the number of emails that person sent or received in the data set.
    This dataframe should be sorted by the number of emails sent.

    :param df: Input dataframe as specified in the excercise document
    :return: the summary statistics
    '''

    # get senders
    emails_sent = [str(i) for i in df['sender']]
    senders = list(set(emails_sent))
    emails_received = [str(i).split("|") for i in df['recipient']]
    emails_received = list(itertools.chain(*emails_received))
    # get recipient#
    recipients = list(set(emails_received))
    sender_ctr = collections.Counter(emails_sent)
    recipient_ctr = collections.Counter(emails_received)
    people = list(set(senders + recipients))
    res = [[person, sender_ctr[person], recipient_ctr[person]] for person in people]
    return pd.DataFrame(res, columns=['person', 'sent', 'received']).sort_values(by=['sent'], ascending=False)


def get_top_senders_graph(df, top_senders):
    '''
        produces a graph image visualizing the number of emails sent over time by some of the most prolific senders.
        There are no specific guidelines regarding the format and specific content of the visualization---
        how many senders to include is defined by constant (maybe we can move in config file),
        Emails are grouped by Quarters.
        :param df: the origianl dataframe
        :param top_senders: list of top senders
        :return: a graph with the emails sent by the top senders
        '''
    # subsample
    res = df[df['sender'].isin(top_senders)]
    # group
    emails_by_quarter = res.groupby([pd.Grouper(freq='BQS-JAN', closed='left'), 'sender']).sender.count() \
        .unstack(fill_value=0)
    # plot
    ts_plot = emails_by_quarter.plot(
        kind='line',
        figsize=(10, 6),
        title="Top Senders By Quarter - Emails Sent",
        linewidth=2.0
    )

    return ts_plot


def get_top_senders_received(df, top_senders):
    '''
    produces a visualization that shows, for the top_senders,
    the number of unique people/email addresses who contacted them over the same time period.
    The counts are stacked to point out the relative numbers of unique incoming contacts
    and how they change quarter by quarter.
    :param df: the origianl dataframe
    :param top_senders: list of top senders
    :return: a graph with the emails received by the top senders
    '''
    # subsample
    emails_received = [str(i).split("|") for i in df['recipient']]
    res = pd.DataFrame(data=None, columns=df.columns)
    for sender in top_senders:
        is_receiver = [sender in p for p in emails_received]
        tmp = df[is_receiver].copy()
        tmp['recipient'] = sender
        res = pd.concat([res, tmp])
    # group
    emails_by_quarter = res.groupby([pd.Grouper(freq='BQS-JAN', closed='left'), 'recipient']).sender.nunique().unstack(
        fill_value=0)
    # plot
    tr_plot = emails_by_quarter.plot(
        kind='bar', stacked=True,
        figsize=(10, 6),
        title="Top Senders By Quarter - Unique Emails Received",
        linewidth=2.0
    )
    # Fix ticklabels as barplot is not that nice
    ticklabels = [''] * len(emails_by_quarter.index)
    ticklabels = [item.strftime('%b') for item in emails_by_quarter.index]
    # Every 4th ticklable shows the year
    ticklabels[1::4] = [item.strftime('%b\n%Y') for item in emails_by_quarter.index[1::4]]
    tr_plot.xaxis.set_major_formatter(ticker.FixedFormatter(ticklabels))
    plt.gcf().autofmt_xdate()
    return tr_plot


def main(_):
    # check args
    if 2 != len(sys.argv):
        print_instructions()
        sys.exit(1)

    # prepare filenames using input filename as base (not the nicest thing but hopefully it will never see production)
    filename = sys.argv[1]
    path = Path(filename).resolve()
    base = path.parent.joinpath(path.stem)
    summary_file = str(base) + "-summary.csv"
    top_sender_sent_file = str(base) + "-top-sender-sent.png"
    top_sender_received_file = str(base) + "-top-sender-received.png"

    # read data
    print("Loading Data...")
    try:
        df = pd.read_csv(filename,
                         names=["time", "id", "sender", "recipient", "topic", "mode"],
                         dtype={"id": np.str, "sender": np.str, "recipient": np.str, "topic": np.str, "mode": np.str},
                         date_parser=dateparser, parse_dates=True, index_col='time',
                         header=None
                         )
    except FileNotFoundError as e:
        print("Error: File {filename} not found".format(filename=sys.argv[1]))
        sys.exit(-1)
    # drop extra columns
    df = df.drop(['id', 'topic', 'mode'], axis=1)

    # get summaries
    print("Getting Summary Statistics...")
    summary = get_summaries(df)
    summary.to_csv(summary_file, index=False)

    # get plot senders sent
    print("Preparing Top Senders Sent Graph...")
    top_senders = list(summary['person'][0:TOP_SENDERS])
    ts_plot = get_top_senders_graph(df, top_senders)
    fig = ts_plot.get_figure()
    fig.savefig(top_sender_sent_file)

    # get plot senders received
    print("Preparing Top Senders Received Graph...")
    tr_plot = get_top_senders_received(df, top_senders)
    fig = tr_plot.get_figure()
    fig.savefig(top_sender_sent_file)

    print("Done!")
    # comment out to inhibit visualization of graphs
    plt.show()


if __name__ == '__main__':
    app.run(main)
