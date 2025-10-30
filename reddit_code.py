
# reddit_code.py
# ------------------------------------------------------
# Reddit API Data Collection Pipeline
# Author: Anshu Mishra
# Course: MSBA 212 – Social Media Analytics
# Institution: California State University, Sacramento
# Instructor: Professor Joseph Richards
#
# This script connects to the Reddit API using PRAW,
# collects "Hot" posts and keyword search results
# from multiple subreddits, cleans and deduplicates
# the data, and exports it as reddit_data.csv.
# ------------------------------------------------------

import os
import time
from typing import List, Dict, Optional
import pandas as pd
import praw
from dotenv import load_dotenv
from urllib.parse import urlparse


# Define the expected output columns
REQUIRED_COLUMNS = [
    "title",
    "score",
    "upvote_ratio",
    "num_comments",
    "author",
    "subreddit",
    "url",
    "permalink",
    "created_utc",
    "is_self",
    "selftext",
    "flair",
    "domain",
    "search_query",
]


def load_reddit_from_env(env_path: str = "reddit.env") -> praw.Reddit:
    """
    Load Reddit API credentials from an environment file and initialize a PRAW client.
    """
    load_dotenv(env_path)

    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT")

    if not all([client_id, client_secret, user_agent]):
        raise ValueError("Missing Reddit credentials. Check your reddit.env file.")

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
        ratelimit_seconds=5,
    )
    return reddit


def safe_get_domain(url_value: Optional[str]) -> Optional[str]:
    """Extract the domain name safely from a URL."""
    if not url_value:
        return None
    try:
        return urlparse(url_value).netloc
    except Exception:
        return None


def submission_to_row(submission, search_query: Optional[str] = None) -> Dict:
    """Convert a Reddit submission object to a clean dictionary row."""
    author_name = getattr(submission.author, "name", None) if submission.author else None
    body = getattr(submission, "selftext", None)
    if body:
        body = body[:500]  # truncate body to 500 characters

    return {
        "title": getattr(submission, "title", None),
        "score": getattr(submission, "score", None),
        "upvote_ratio": getattr(submission, "upvote_ratio", None),
        "num_comments": getattr(submission, "num_comments", None),
        "author": author_name,
        "subreddit": str(getattr(submission, "subreddit", "")),
        "url": getattr(submission, "url", None),
        "permalink": f"https://www.reddit.com{getattr(submission, 'permalink', '')}",
        "created_utc": int(getattr(submission, "created_utc", 0))
        if getattr(submission, "created_utc", None)
        else None,
        "is_self": getattr(submission, "is_self", None),
        "selftext": body,
        "flair": getattr(submission, "link_flair_text", None),
        "domain": safe_get_domain(getattr(submission, "url", None)),
        "search_query": search_query,
    }


def collect_hot_posts(reddit: praw.Reddit, subreddits: List[str], limit_per_sub: int) -> List[Dict]:
    """Collect 'Hot' posts from multiple subreddits."""
    rows: List[Dict] = []
    total = 0

    for sr in subreddits:
        print(f"Collecting 'Hot' posts from r/{sr} ...")
        try:
            for sub in reddit.subreddit(sr).hot(limit=limit_per_sub):
                rows.append(submission_to_row(sub))
                total += 1
            print(f"✓ Done r/{sr}: {limit_per_sub} posts")
            time.sleep(1)
        except Exception as e:
            print(f"Skipping r/{sr} due to error: {e}")

    print(f"Total 'Hot' posts collected: {total}\n")
    return rows


def collect_search_posts(
    reddit: praw.Reddit, subreddits: List[str], query: str, limit_per_sub: int
) -> List[Dict]:
    """Search for specific keywords across multiple subreddits."""
    rows: List[Dict] = []
    total = 0

    for sr in subreddits:
        print(f"Searching '{query}' in r/{sr} ...")
        try:
            for sub in reddit.subreddit(sr).search(query, limit=limit_per_sub):
                rows.append(submission_to_row(sub, search_query=query))
                total += 1
            print(f"✓ Done r/{sr}: {limit_per_sub} posts for keyword '{query}'")
            time.sleep(1)
        except Exception as e:
            print(f"Search failed for r/{sr}: {e}")

    print(f"Total posts found for keyword '{query}': {total}\n")
    return rows


def save_clean_csv(rows: List[Dict], out_path: str = "reddit_data.csv") -> None:
    """Convert collected rows into a DataFrame, remove duplicates, and save as CSV."""
    df = pd.DataFrame(rows)
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = None
    df = df[REQUIRED_COLUMNS]

    before = len(df)
    df = df.drop_duplicates(subset=["permalink"]).reset_index(drop=True)
    after = len(df)

    print(f"Removed {before - after} duplicates. {after} unique posts saved.")
    df.to_csv(out_path, index=False)
    print(f"CSV saved successfully as {out_path}\n")


def main():
    """Main execution function."""
    print("Starting Reddit data collection...\n")

    reddit = load_reddit_from_env("reddit.env")

    # --- EDIT THIS SECTION WITH YOUR OWN THEME ---
    TOPIC_SUBREDDITS = ["Depression", "Anxiety", "Meditation"]
    SEARCH_KEYWORDS = ["therapy", "mindfulness", "mental health"]
    POST_LIMIT = 50
    # ------------------------------------------------

    # Collect Hot posts
    hot_rows = collect_hot_posts(reddit, TOPIC_SUBREDDITS, POST_LIMIT)

    # Collect Search posts for each keyword
    search_rows = []
    for keyword in SEARCH_KEYWORDS:
        search_rows.extend(collect_search_posts(reddit, TOPIC_SUBREDDITS, keyword, POST_LIMIT))

    # Combine and save all collected data
    all_rows = hot_rows + search_rows
    save_clean_csv(all_rows, out_path="reddit_data.csv")

    print("Data collection complete. Check reddit_data.csv for output.\n")


if __name__ == "__main__":
    main()

