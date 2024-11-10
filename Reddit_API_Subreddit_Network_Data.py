import pandas as pd
import praw
from prawcore.exceptions import RequestException
import warnings
warnings.filterwarnings("ignore")

def create_network_dataset(topic, limit):
    reddit = praw.Reddit(client_id='a9v5PHHA_RbXrkcBR6q53g',
                         client_secret='FsbKnWL73NRomxFT4vBxLujSuMVX9Q',
                         user_agent='content_rec')

    data = {}

    for subreddit in reddit.subreddits.search(topic, limit=limit):
        try:
            print(f"Collecting network data from subreddit: {subreddit.display_name}")

            post_authors = []
            comment_authors = []

            for post in subreddit.top('all', limit=10):
                if post.author is None:
                    continue
                post_authors.append(post.author.name)

                post.comments.replace_more(limit=0)
                for comment in post.comments.list():
                    if comment.author is None:
                        continue
                    comment_authors.append(comment.author.name)

            data[subreddit.display_name] = {
                'PostAuthors': list(set(post_authors)),
                'CommentAuthors': list(set(comment_authors))
            }

        except RequestException as e:
            if e.response.status_code in [403, 404, 429]:
                print(f"Error for {subreddit.display_name}, skipping.")
                continue
            else:
                print(f"An error occurred: {e}")

    network_df = pd.DataFrame.from_dict(data, orient='index').reset_index()
    network_df.rename(columns={'index': 'Subreddit'}, inplace=True)

    return network_df

topic = input("Enter the type of subreddit you are interested in: ")
limit = int(input("How many subreddits do you want to consider for your network dataset? "))

network_df = create_network_dataset(topic, limit)

network_df.to_csv("subreddit_network_data.csv", index=False)
print(network_df.head())