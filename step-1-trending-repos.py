import os
import requests
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict

def fetch_trending_topics(github_token: str, days: int = 30, min_stars: int = 100) -> Dict[str, Dict]:
    """
    Fetch topics from top repositories created in the last n days.
    Returns a dictionary of topics with their repository counts and total stars.
    """
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    date_threshold = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    url = 'https://api.github.com/search/repositories'
    params = {
        'q': f'created:>{date_threshold} stars:>{min_stars}',
        'sort': 'stars',
        'order': 'desc',
        'per_page': 100
    }

    topics_data = defaultdict(lambda: {
        'repos': 0,
        'total_stars': 0
    })
    
    try:
        print("Fetching repositories from GitHub...")
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        repos = response.json()['items']

        print(f"Processing {len(repos)} repositories...")
        for repo in repos:
            stars = repo['stargazers_count']
            for topic in repo.get('topics', []):
                topics_data[topic]['repos'] += 1
                topics_data[topic]['total_stars'] += stars

        return dict(topics_data)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching GitHub repositories: {e}")
        return {}

def main():
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        raise ValueError("Please set the GITHUB_TOKEN environment variable")

    # Fetch topics data
    topics_data = fetch_trending_topics(github_token)
    
    # Print top 10 topics by number of repositories
    print("\n=== Top 10 Topics by Repository Count ===\n")
    sorted_topics = sorted(
        topics_data.items(), 
        key=lambda x: x[1]['repos'], 
        reverse=True
    )[:10]
    
    for topic, data in sorted_topics:
        print(f"Topic: {topic}")
        print(f"Repositories: {data['repos']}")
        print(f"Total Stars: {data['total_stars']}")
        print()

if __name__ == "__main__":
    main()