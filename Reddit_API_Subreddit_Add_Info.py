import pandas as pd
import praw
from prawcore.exceptions import RequestException
import warnings
warnings.filterwarnings("ignore")

def create_sub_dataset(topic, limit):
    reddit = praw.Reddit(client_id='a9v5PHHA_RbXrkcBR6q53g',
                         client_secret='FsbKnWL73NRomxFT4vBxLujSuMVX9Q',
                         user_agent='content_rec')

    dataset = []

    for subreddit in reddit.subreddits.search(topic, limit=limit):
        try:
            print(f"Searching in subreddit: {subreddit.display_name}")
            top_10_posts = []
            top_10_comments = []
            karma = 0
            cross_posting_subreddits = set()

            for post in subreddit.top('all', limit=10):
                top_10_posts.append(post.title)
                karma += post.score

                post.comment_sort = 'top'
                post.comments.replace_more(limit=0)
                top_comments = []
                for comment in post.comments[:20]:
                    top_comments.append(comment.body)
                top_10_comments.append(top_comments)

                if hasattr(post, 'crosspost_parent_list'):
                    for crosspost in post.crosspost_parent_list:
                        cross_posting_subreddits.add(crosspost['subreddit'])

            dataset.append({
                "Subreddit": subreddit.display_name,
                "Top 10 Posts": top_10_posts,
                "Top 10 Comments": [comment for sublist in top_10_comments for comment in sublist],
                "Karma": karma,
                "Cross-Posting Subreddits": list(cross_posting_subreddits)
            })

        except RequestException as e:
            if e.response.status_code in [403, 404, 429]:
                print(f"Error for {subreddit.display_name}, skipping.")
                continue
            else:
                print(f"An error occurred: {e}")

        except Exception as e:
            print(f"An error occurred: {e}")

    df = pd.DataFrame(dataset)
    return df

topic = input("Enter the type of subreddit you are interested in: ")
limit = int(input("How many subreddits do you want to consider for your dataset? "))

df = create_sub_dataset(topic, limit)


df.to_csv("subreddit_data_add_info.csv", index=False)
print(df.head())