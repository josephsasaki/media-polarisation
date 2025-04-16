# Tilt Media Bias Dashboard

This repository contains a Streamlit-based interactive dashboard that visualizes and analyzes media bias across different news organizations. The dashboard allows users to explore daily and historical trends in sentiment, subjectivity, and polarity of news articles.

---

##  Project Structure

- `welcome.py`: The main entry point for the dashboard. It displays the logo, title, and an introduction to the available pages and metrics.
- `pages/`: Contains the sub-pages of the dashboard, each providing specific insights:
  - **Key Metrics for Each Day Page**: Shows article and topic metrics per paper on a given day.
  - **Subjectivity Page**: Displays articles with the highest positive and negative subjectivity scores.
  - **Overall Articles Page**: Presents longer-term metrics, including sentiment distribution across articles.
  - **Metrics Explanation Page**: Explains all the analytical metrics used in the dashboard.

---

##  Metrics Overview

- **Sentiment**: Includes positive, negative, neutral, and compound scores. The *compound* score measures the overall sentiment intensity.
- **Subjectivity**: Reflects how emotive or opinionated the language is. Example:  
  - *Objective*: "Hot chocolate is a popular beverage."  
  - *Subjective*: "Hot chocolate is tolerated by the masses."
- **Polarity**: Represents sentiment without intensity. Example:  
  - "I don't like that." and "I HATE THAT." have the same polarity but different sentiment intensity.

---

## **Environment Variables**

Ensure the following environment variables are set up either in your Lambda environment or in a `.env` file:

- **`DB_HOST`**: Hostname of the PostgreSQL RDS instance.
- **`DB_PORT`**: Port number for the database (default: `5432`).
- **`DB_USERNAME`**: Username to connect to the database.
- **`DB_PASSWORD`**: Password for the database user.
- **`DB_NAME`**: Name of the database to connect to.

---

##  Running the Dashboard Locally

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/tilt-dashboard.git
   cd tilt-dashboard
