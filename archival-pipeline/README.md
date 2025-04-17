# Archival Pipeline

The archival pipeline extracts article data from the AWS RDS Postgresql database once it is over 6 months old, it then transforms the data and loads it into the AWS S3 Bucket. The pipeline is designed to be run on a AWS Lambda function which when triggered performs the archival process. The following repository contains code needed for the image to run on the archival lambda.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Project Structure](#project-structure)

## Features

- ✅ Extracts the article and topic data and it's sentiment analysis scores.
- ✅ Transforms the extracted data into objects, with cleaned and quality-assured attributes.
- ✅ Loads the data to a S3 Bucket.

## Installation

Clone the repository:

```bash
git clone https://github.com/josephsasaki/media-polarisation
cd archival-pipeline
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
```

Make sure to include your `.env` in a `.gitignore` file.

## Project Structure

```text
archival-pipeline/
.
├── .env                # Environment variables file created by user
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── archiver.py         # Script for running the entire archival pipeline
├── database_manager.py          # Script for extracting article data from the database
├── Dockerfile          # File for dockerising the code for AWS Lambda
├── s3_manager.py   # Script for defining the class that interacts with the aws s3 bucket
├── transformer.py   # Script for transforming the data so it is ready to be loaded into the s3
├── test_database_manager.py        # Unit-testing for loading
├── test_transformer.py      # Unit-testing for models
├── test_s3_manager.py   # Unit-testing for transforming
```

