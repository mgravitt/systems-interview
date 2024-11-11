# Challenge Overview
1. Query Github API to find list of trending repositories with topics
2. Query HackerNews API to find discussions for each topic
3. Analyze and score trends to determine overall top 10 topics

## Step 1: Query Github API to find list of trending repositories
Documentation here: https://docs.github.com/en/rest/search/search?apiVersion=2022-11-28

### How do find trending repositories?
Tips: 
- Use the `q` parameter to search for trending repositories
- Use the `created` parameter within the `q` parameter to filter by date, e.g. last 7 days
- Use the `stars` parameter within the `q` parameter to filter by number of stars, e.g. more than 100 stars
- Sort the results by `stars`

#### Step 1.1: Authenticate with Github API
Part of the challenge is for the interviewee to figure out how to authenticate with the Github API based on reading docs. If they seem to get stuck, you can provide them the curl command: 
```
curl -H "Accept: application/vnd.github.v3+json" \
     -H "Authorization: token GITHUB_TOKEN" \
     "https://api.github.com/search/repositories?q=org:github&per_page=30"
```
The command above returns a list of repositories for the Github organization.

#### Step 1.2: Get the `q` parameter correct
The `q` parameter is the most important part of this step. The interviewee needs to figure out how to use the `created` and `stars` parameters correctly. 
```
curl -H "Accept: application/vnd.github.v3+json" \
     -H "Authorization: token GITHUB_TOKEN" \
     "https://api.github.com/search/repositories?q=created:>2024-11-01+stars:>100&sort=stars&order=desc&per_page=30"
```

#### Step 1.3: Parse the response
The response is a JSON object. The interviewee needs to figure out how to parse the response and extract the relevant information. The important information for the overall challenge is the `topics` field, but certainly more can be parsed.

### For a Python solution, see `step-1-trending-repos.py`

## Step 2: Query HackerNews API to find discussions for each topic
Documentation here: https://hn.algolia.com/api

### Step 2.1: Query the search endpoint
The HackerNews API does not require authentication.
```
curl "https://hn.algolia.com/api/v1/search?query=bitcoin&tags=story&numericFilters=created_at_i>2024-11-01"
```
