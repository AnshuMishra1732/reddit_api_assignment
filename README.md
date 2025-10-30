# Reddit API Data Collection Assignment

This project connects to the Reddit API using PRAW (Python Reddit API Wrapper) to collect, process, and export Reddit posts related to a chosen topic.  
It demonstrates how to securely access APIs, clean data using pandas, and create a simple data pipeline for analysis.

---

## Assignment Overview
The goal of this project is to build a Python application that interacts with the Reddit API to collect, clean, and store social media data from several subreddits.  
This assignment simulates a real-world data engineering and analytics workflow, where you design a small data collection pipeline.

The script:
- Connects to the Reddit API using credentials stored securely in an environment file (`reddit.env`)
- Fetches "Hot" posts from multiple subreddits
- Performs keyword-based searches across the same subreddits
- Cleans and merges the collected data
- Removes duplicates and exports the final dataset as a clean CSV file for analysis

---

## Learning Objectives
By completing this project, I learnt to: 
- Understanding how to authenticate and interact with a public API
- Apply object-oriented programming to organize data collection logic
- Use pandas for data cleaning, deduplication, and file export
- Implement secure credential management using environment variables
- Gain experience with GitHub version control and reproducible code practices

---

## How to Run the Project

### 1. Requirements
- Python 3.8+
- Installed libraries: `praw`, `pandas`, `python-dotenv`

If not already installed, run:
```bash
pip install -r requirements.txt

