# Dispatcher

The scraper pipeline extracts article data from news RSS feeds, performs sentiment analysis on the text, then loads the data to the database. The pipeline is designed to be run on a set of AWS Lambda functions, in which a dispatcher Lambda invokes worker lambdas to complete the data pipeline. The following repository contains code needed for the image run on the dispatcher Lambda. See `media-polarisation/scraper-pipeline/pipeline` for the code needed in the worker Lambdas.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Project Structure](#project-structure)

## Features

- ✅ Contains a `lambda_handler` function run by the AWS Lambda which invokes other Lambda functions to run. These Lambda's would presumably be build with the pipeline image.
- ✅ This configuration of multiple worker Lambdas massively reduces runtime.

## Installation

Clone the repository:

```bash
git clone https://github.com/josephsasaki/media-polarisation
cd scraper-pipeline/dispatcher
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

The pipeline is designed to be dockerised using the provided Dockerfile, and pushed to AWS's ECR. From there, the dispatcher can be run from a Lambda. 

## Configuration

It is recommended a `.env` file is created, and the following environment variables are defined:

```
ACCESS_KEY=your_aws_access_key
SECRET_ACCESS_KEY=your_aws_secret_access_key
LAMBDA_REGION=your_lambdas_region
WORKER_FUNCTION_NAME=your_worker_lambda_name
```

Make sure to include your `.env` in a `.gitignore` file.

## Project Structure

```text
pipeline/
.
├── .env                # Environment variables file created by user
├── Dockerfile          # File for dockerising the code for AWS Lambda
├── README.md           # This file
├── lambda_handler.py   # Entry-point for AWS Lambda
└── requirements.txt    # Python dependencies
```