from jira import JIRA
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import pandas as pd
import matplotlib.pyplot as plt

# Connect to JIRA
jira = JIRA(server='https://opengovinc.atlassian.net/', 
            basic_auth=('scheriyakummeri@opengov.com', 'Token'))


jql_query = 'project = CRD AND "Suite[Dropdown]" = Financials'

# Fetch JIRA tickets
tickets = jira.search_issues(jql_query, maxResults=500)

# Extract ticket summaries, descriptions, and comments
ticket_data = []
for issue in tickets:
    # Get comments for each issue
    comments = jira.comments(issue)
    comment_text = " ".join([comment.body for comment in comments])

    ticket_data.append({
        'key': issue.key,
        'summary': issue.fields.summary,
        'description': issue.fields.description,
        'comments': comment_text  # Concatenate all comments
    })

# Convert to DataFrame
df = pd.DataFrame(ticket_data)

# Combine the summary, description, and comments into a single text feature for analysis
df['full_text'] = df['summary'] + ' ' + df['description'].fillna('') + ' ' + df['comments'].fillna('')

# Preprocess and Vectorize the text data
vectorizer = TfidfVectorizer(max_features=1000)
X = vectorizer.fit_transform(df['full_text'])

# Define the number of clusters (for K-Means, this needs to be pre-defined, adjust based on use case)
n_clusters = 3  # Example: grouping into 3 clusters (adjust this based on how many categories you want)

# Apply K-Means clustering
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
df['cluster'] = kmeans.fit_predict(X)

# Optional: Visualize clusters using PCA (for 2D visualization)
pca = PCA(n_components=2)
reduced_X = pca.fit_transform(X.toarray())

plt.scatter(reduced_X[:, 0], reduced_X[:, 1], c=df['cluster'], cmap='viridis')
plt.title('Ticket Clusters (K-Means)')
plt.xlabel('PCA Component 1')
plt.ylabel('PCA Component 2')
plt.colorbar(label='Cluster Label')
plt.show()

# Display ticket clusters
for cluster_num in range(n_clusters):
    print(f"\nCluster {cluster_num}:")
    print(df[df['cluster'] == cluster_num][['key', 'summary', 'description']].head())  # Display a few tickets from each cluster
