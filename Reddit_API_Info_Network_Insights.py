import numpy as np
import pandas as pd
import networkx as nx
import csv
import praw
from prawcore.exceptions import RequestException
from textblob import TextBlob
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
            G = nx.Graph()
            top_posts = list(subreddit.top('all', limit=10))
            if top_posts:
                for post in top_posts:
                    if post.author:
                        G.add_node(post.author.name)
                        post.comments.replace_more(limit=0)
                        for comment in post.comments.list():
                            if comment.author:
                                G.add_node(comment.author.name)
                                G.add_edge(post.author.name, comment.author.name)


                num_nodes = G.number_of_nodes()
                num_edges = G.number_of_edges()
                average_degree = np.mean([degree for node, degree in G.degree()])
                average_nw_density = nx.density(G)
                highly_connected_nodes_no = len([node for node, degree in G.degree() if degree > average_degree])
                sparsely_connected_nodes_no = len([node for node, degree in G.degree() if degree < average_degree])
                giant_connected_component = max(nx.connected_components(G), key=len)
                diameter_nw = nx.diameter(G.subgraph(giant_connected_component))
                avg_shortest_path_length = nx.average_shortest_path_length(G.subgraph(giant_connected_component))
                avg_degree_centrality = np.mean(list(nx.degree_centrality(G).values()))
                std_dev_degree_centrality = np.std(list(nx.degree_centrality(G).values()))
                avg_closeness_centrality = np.mean(list(nx.closeness_centrality(G).values()))
                avg_betweenness_centrality = np.mean(list(nx.betweenness_centrality(G).values()))
                clustering_coefficient = nx.average_clustering(G)
                modularity = nx.community.modularity(G, nx.community.label_propagation_communities(G))
                avg_degree_ditribution = np.mean(list(nx.degree_histogram(G)))

                total_post_count = len(top_posts)
                total_gilded_post_count = len([post for post in top_posts if post.gilded])
                average_score = np.mean([post.score for post in top_posts])
                average_upvote_ratio = np.mean([post.upvote_ratio for post in top_posts])
                average_num_comments = np.mean([post.num_comments for post in top_posts])
                sentiment_scores = np.mean([TextBlob(post.title).sentiment.polarity for post in top_posts])
                average_post_length = np.mean([len(post.title.split()) for post in top_posts])


                dataset.append({
                    "Subreddit": subreddit.display_name,
                    "Subreddit Description": subreddit.public_description,
                    "Total Subscribers": subreddit.subscribers,
                    "Total Post Count": total_post_count,
                    "Total Gilded Post Count": total_gilded_post_count,
                    "Average Score": average_score,
                    "Average Upvote Ratio": average_upvote_ratio,
                    "Average Comments": average_num_comments,
                    "Average Post Length": average_post_length,
                    "Sentiment Scores": sentiment_scores,
                    "Number of Nodes": num_nodes,
                    "Number of Edges": num_edges,
                    "Average Degree": average_degree,
                    "Average Network Density": average_nw_density,
                    "Highly Connected Nodes": highly_connected_nodes_no,
                    "Sparsely Connected Nodes": sparsely_connected_nodes_no,
                    "Giant Connected Component": giant_connected_component,
                    "Diameter of Network": diameter_nw,
                    "Average Shortest Path Length": avg_shortest_path_length,
                    "Average Degree Centrality": avg_degree_centrality,
                    "Standard Deviation of Degree Centrality": std_dev_degree_centrality,
                    "Average Closeness Centrality": avg_closeness_centrality,
                    "Average Betweenness Centrality": avg_betweenness_centrality,
                    "Clustering Coefficient": clustering_coefficient,
                    "Modularity": modularity,
                    "Average Degree Distribution": avg_degree_ditribution

                })

        except RequestException as e:
            if e.response.status_code in [403, 404, 429]:
                print(f"Error for {subreddit.display_name}, skipping.")
                continue
            else:
                print(f"An error occurred: {e}")

        except Exception as e:
            print(f"An error occurred: {e}")

    if dataset:
        with open('subreddit_data_info_nw_insights.csv', 'w', newline='', encoding='utf-8') as file:
            fieldnames = ["Subreddit", "Subreddit Description", "Total Subscribers", "Average Active Users", "Total Post Count", "Total Gilded Post Count",
                          "Average Score", "Average Upvote Ratio", "Average Comments", "Average Post Length", "Sentiment Scores", "Number of Nodes",
                          "Number of Edges", "Average Degree", "Average Network Density", "Highly Connected Nodes", "Sparsely Connected Nodes",
                          "Giant Connected Component", "Diameter of Network", "Average Shortest Path Length", "Average Degree Centrality",
                          "Standard Deviation of Degree Centrality", "Average Closeness Centrality", "Average Betweenness Centrality",
                          "Clustering Coefficient", "Modularity", "Average Degree Distribution"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for row in dataset:
                writer.writerow(row)
        print("Dataset created successfully.")

    else:
        print("No data was collected. Please check your topic or try again later.")

    return pd.DataFrame(dataset)


topic = input("Enter the type of subreddit you are interested in: ")
limit = int(input("How many subreddits do you want to consider for your dataset? "))
data = create_sub_dataset(topic, limit)
print(data.head())

# data.to_csv("subreddit_data_info_nw_insights.csv", index=False)
# print(data.head())

