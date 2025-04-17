# **Daily Email Report - Sentiment Analysis from RDS**

This project contains Python scripts to generate a daily email report based on sentiment analysis data stored in a PostgreSQL RDS database. The report compares the sentiment of articles from two major outlets—The Guardian and The Daily Express—based on pre-analyzed sentiment data already stored in the database. The generated report includes sentiment trends, topic frequencies, and the most polarizing articles.

### **Directory Overview**

- **`report_generator.py`**: The main script that queries the PostgreSQL RDS database for sentiment analysis data, generates the report (HTML and PDF), and emails it.
  
- **`queries.py`**: Contains SQL queries used to extract sentiment data from the database. This includes queries for sentiment by topic, top articles, and outlet sentiment.

- **`report_creator.py`**: A class that assembles the report, formats the data retrieved from the database, generates visualizations (like charts), and renders the report in HTML and PDF formats.

- **`lambda_handler.py`**: The AWS Lambda function's entry point. It triggers the process of generating and sending the daily report when invoked.

- **`requirements.txt`**: A file that lists Python dependencies required to run the scripts.

- **`Dockerfile`**: Provides instructions to containerize the Lambda function, install dependencies, and run the `lambda_handler.py`.

- **`template/`**: Contains HTML templates for rendering the daily report.

---

## **Environment Variables**

Ensure the following environment variables are set up either in your Lambda environment or in a `.env` file:

- **`DB_HOST`**: Hostname of the PostgreSQL RDS instance.
- **`DB_PORT`**: Port number for the database (default: `5432`).
- **`DB_USERNAME`**: Username to connect to the database.
- **`DB_PASSWORD`**: Password for the database user.
- **`DB_NAME`**: Name of the database to connect to.
- **`AWS_ACCESS_KEY`**: AWS access key for sending email via SES.
- **`AWS_SECRET_ACCESS_KEY`**: AWS secret key for sending email via SES.
- **`SES_EMAIL_ADDRESS`**: The email address that will send the report.

---

## **How It Works**

1. **Data Retrieval**: The `report_generator.py` script queries the PostgreSQL RDS database for pre-analyzed sentiment data, including:
   - Sentiment scores by topic.
   - Frequency of topics covered by each outlet.
   - The most polarizing articles based on sentiment.
   - Overall sentiment scores for The Guardian and The Daily Express.

2. **Report Creation**: The `report_creator.py` script formats the data retrieved from the database into a visually appealing report. The report is generated as both an HTML file (for visual review) and a PDF (for emailing).

3. **Email Distribution**: Once the report is generated, the `lambda_handler.py` script sends the report as an email using AWS SES, with the HTML and PDF reports attached.

---

