import os
import requests
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict
import time

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

def get_hackernews_data(topic: str, days: int = 30) -> Dict[str, int]:
    """
    Search HackerNews for discussions about a topic and return metrics.
    """
    timestamp_threshold = int((datetime.now() - timedelta(days=days)).timestamp())
    
    url = 'https://hn.algolia.com/api/v1/search'
    params = {
        'query': topic,
        'numericFilters': f'created_at_i>{timestamp_threshold}',
        'tags': 'story'
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        hits = response.json()['hits']

        return {
            'items_count': len(hits),
            'total_score': sum(hit.get('points', 0) for hit in hits if hit.get('points'))
        }

    except requests.exceptions.RequestException as e:
        print(f"Error fetching HackerNews data for {topic}: {e}")
        return {'items_count': 0, 'total_score': 0}

def main():
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        raise ValueError("Please set the GITHUB_TOKEN environment variable")

    # Get GitHub topics data
    topics_data = fetch_trending_topics(github_token)
    
    # Add HackerNews data for each topic
    print("\nFetching HackerNews data for each topic...")
    for topic in topics_data:
        print(f"Processing topic: {topic}")
        hn_data = get_hackernews_data(topic)
        topics_data[topic]['hackernews'] = hn_data
        time.sleep(0.01)  # Small delay to avoid rate limiting
    
    # Print results
    print("\n=== Top Topics with GitHub and HackerNews Data ===\n")
    # Sort by combined GitHub repos and HN items
    sorted_topics = sorted(
        topics_data.items(),
        key=lambda x: (x[1]['repos'] + x[1]['hackernews']['items_count']),
        reverse=True
    )[:10]
    
    for topic, data in sorted_topics:
        print(f"Topic: {topic}")
        print(f"GitHub: {data['repos']} repos, {data['total_stars']} stars")
        print(f"HackerNews: {data['hackernews']['items_count']} items, "
              f"{data['hackernews']['total_score']} points")
        print()

if __name__ == "__main__":
    main()