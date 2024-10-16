from jira import JIRA
import requests
import json
import pandas as pd
import spacy

# JIRA API details
# Connect to JIRA
jira = JIRA(server='https://opengovinc.atlassian.net/', 
            basic_auth=('scheriyakummeri@opengov.com', 'ATATT3xFfGF0KCvm32jAq0UZiefqz6ALngDFY_pJ01YBQkB2YjfhJc9XrbTxpR6um9BQSL7w6JhInjMB2pMP6hSZNwlWCESJsLG8ydCc-bk5y8kfB3X31XfgqgagjmZoNqvUpfA6FVh1PNgZIVs_ujH3NWix_wLWekfWMHZOJJtWw7V4WmY3X58=0071E05B'))


jql_query = 'project = CRD AND "Suite[Dropdown]" = Financials'

# Fetch JIRA tickets
tickets = jira.search_issues(jql_query, maxResults=500)


nlp = spacy.load('en_core_web_sm')

# Preprocess ticket descriptions for analysis
def preprocess_text(text):
    doc = nlp(text.lower())
    return ' '.join([token.lemma_ for token in doc if not token.is_stop])

# Example preprocessing
# Assuming 'tickets' is a list of Issue objects from the JIRA API
preprocessed_tickets = [preprocess_text(ticket.fields.description) for ticket in tickets if ticket.fields.description]


def classify_ticket(description):
    description = description.lower()
    
    # Keywords for each category
    feature_keywords = ['enhance', 'improve', 'add']
    bug_keywords = ['error', 'bug', 'issue', 'fix']
    tech_error_keywords = ['failure', 'technical', 'exception']
    
    # Categorization based on keyword matching
    if any(keyword in description for keyword in feature_keywords):
        return 'Feature Enhancement'
    elif any(keyword in description for keyword in bug_keywords):
        return 'Bug'
    elif any(keyword in description for keyword in tech_error_keywords):
        return 'Technical Error'
    else:
        return 'Unknown'

# Classify each ticket
# Assuming 'tickets' is a list of Issue objects
ticket_classifications = [classify_ticket(ticket.fields.description) for ticket in tickets if ticket.fields.description]


# Prepare the data for export
data = []
for ticket, classification in zip(tickets, ticket_classifications):
    data.append({
        'Ticket ID': ticket.key,
        'Summary': ticket.fields.summary,
        'Description': ticket.fields.description,
        'Classification': classification
    })


# Create a DataFrame and save it to an Excel file
df = pd.DataFrame(data)
df.to_excel('jira_ticket_classifications.xlsx', index=False)
print("Excel file has been created: jira_ticket_classifications.xlsx")


