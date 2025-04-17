# Scraper Pipeline

The scraper pipeline extracts article data from news RSS feeds, performs sentiment analysis on the text, then loads the data to the database. The pipeline is designed to be run on a set of AWS Lambda functions, in which a dispatcher Lambda invokes worker lambdas to complete the data pipeline. The following repository contains code needed for the image run on the worker lambdas. See `media-polarisation/scraper-pipeline/dispatcher` for the code needed in the dispatcher Lambda.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Project Structure](#project-structure)

## Features

- ✅ Extracts raw article data from a set of RSS feeds, and extracts the relevant data needed for sentiment analysis.
- ✅ Transforms the raw data into objects, with cleaned and quality-assured attributes.
- ✅ Analyses the article text: topics are extracted from each article, and sentiment analysis is performed on articles as a whole and the individual topics within articles.
- ✅ Loads the data to a SQL database.

## Installation

Clone the repository:

```bash
git clone https://github.com/josephsasaki/media-polarisation
cd scraper-pipeline/pipeline
```

Set up a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

The pipeline is designed to be dockerised using the provided Dockerfile, and pushed to AWS's ECR. From there, the pipeline can be run from a Lambda. 

## Configuration

It is recommended a `.env` file is created, and the following environment variables are defined:

```
DB_USERNAME=your_database_name
DB_PASSWORD=your_database_password
DB_NAME=your_database_name
DB_HOST=your_database_host
DB_PORT=your_database_port
OPENAI_API_KEY=your_openai_api_key
```

Make sure to include your `.env` in a `.gitignore` file.

## Project Structure

```text
yourproject/
.
├── Dockerfile          # File for dockerising the code for AWS Lambda
├── README.md           
├── analysis.py         # Script for performing analysis on articles
├── extract.py          # Script for extracting article data from RSS feeds
├── lambda_handler.py   # Entry-point for AWS Lambda
├── load.py             # Load the article analysis data to database
├── models.py           # Defines article models
├── requirements.txt    # Python dependencies
├── scraper.py          # Script containing whole pipeline operation
├── test_extract.py     # Unit-testing for extraction
├── test_load.py        # Unit-testing for loading
├── test_models.py      # Unit-testing for models
├── test_transform.py   # Unit-testing for transforming
└── transform.py        # Transform and clean the raw article data into objects
```