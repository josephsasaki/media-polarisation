'''
Script for extracting insights from the rds and writing them up into a report
'''
import os
from datetime import date, timedelta
from base64 import b64encode
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from dotenv import load_dotenv
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import psycopg2.extras
from psycopg2.extensions import connection
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
import boto3
from newspaper import Article


# once we have historic data AND a.article_published_date: : DATE = %s
SENTIMENT_BY_TOPIC_QUERY = '''
                WITH guardian_topics_avg AS (SELECT t.topic_name,
                    AVG(at.article_topic_compound_sentiment::numeric) AS compound
                    FROM article_topic as at
                    JOIN topic AS t ON t.topic_id = at.topic_id
                    JOIN article AS a ON a.article_id = at.article_id
                    JOIN news_outlet AS no ON no.news_outlet_id = a.news_outlet_id
                    WHERE no.news_outlet_name = %s AND a.article_published_date:: DATE = %s
                    GROUP BY t.topic_name),

                express_topics_avg AS (SELECT t.topic_name,
                    AVG(at.article_topic_compound_sentiment::numeric) AS compound
                    FROM article_topic as at
                    JOIN topic AS t ON t.topic_id = at.topic_id
                    JOIN article AS a ON a.article_id = at.article_id
                    JOIN news_outlet AS no ON no.news_outlet_id = a.news_outlet_id
                    WHERE no.news_outlet_name = %s AND a.article_published_date:: DATE = %s
                    GROUP BY t.topic_name)

                    SELECT gta.topic_name, ROUND(gta.compound, 2):: float AS guardian_compound, ROUND(eta.compound, 2):: float AS express_compound, ROUND(ABS(gta.compound - eta.compound),2)::float AS compound_diff
                    FROM guardian_topics_avg gta
                    INNER JOIN express_topics_avg eta ON eta.topic_name = gta.topic_name
                    ORDER BY compound_diff DESC
                    ;'''

MOST_COVERED_TOPIC_QUERY = '''
                    WITH topic_counts AS (
                        SELECT t.topic_name, COUNT(*) AS topic_frequency
                        FROM article_topic AS at
                        JOIN topic AS t ON t.topic_id = at.topic_id
                        JOIN article AS a ON a.article_id = at.article_id
                        JOIN news_outlet AS no ON no.news_outlet_id = a.news_outlet_id
                        WHERE no.news_outlet_name = %s AND a.article_published_date:: DATE = %s
                        GROUP BY t.topic_name
                    ),
                    total_topics AS (
                        SELECT COUNT(*) AS total_count
                        FROM article_topic AS at
                        JOIN article AS a ON a.article_id = at.article_id
                        JOIN news_outlet AS no ON no.news_outlet_id = a.news_outlet_id
                        WHERE no.news_outlet_name = %s AND a.article_published_date:: DATE = %s
                    )

                    SELECT tc.topic_name,
                        ROUND((tc.topic_frequency * 100.0) / tt.total_count, 2) AS topic_percentage
                    FROM topic_counts tc
                    JOIN total_topics tt ON true
                    ORDER BY topic_percentage DESC;
'''

OUTLET_SENTIMENT_QUERY = '''
                    SELECT no.news_outlet_name,
                    ROUND(AVG(at.article_topic_compound_sentiment::numeric), 3)::float AS compound
                    FROM article_topic as at
                    JOIN topic AS t ON t.topic_id = at.topic_id
                    JOIN article AS a ON a.article_id = at.article_id
                    JOIN news_outlet AS no ON no.news_outlet_id = a.news_outlet_id
                    WHERE a.article_published_date:: DATE = %s
                    GROUP BY no.news_outlet_name;'''

TOP_NEGATIVE_ARTICLES = '''
                    SELECT a.article_headline, a.article_url,
                    a.article_compound_sentiment AS sentiment
                    FROM article as a
                    JOIN news_outlet AS no ON no.news_outlet_id = a.news_outlet_id
                    WHERE a.article_published_date:: DATE = %s AND no.news_outlet_name = %s
                    ORDER BY sentiment ASC
                    LIMIT 3;'''

TOP_POSITIVE_ARTICLES = '''
                    SELECT a.article_headline, a.article_url,
                    a.article_compound_sentiment AS sentiment
                    FROM article as a
                    JOIN news_outlet AS no ON no.news_outlet_id = a.news_outlet_id
                    WHERE a.article_published_date:: DATE = %s AND no.news_outlet_name = %s
                    ORDER BY sentiment DESC
                    LIMIT 3;'''

YESTERDAYS_DATE = date.today() - timedelta(days=1)


class ReportCreator:
    '''Class inserting article information and analysis into a rds postgres database '''

    def __init__(self) -> None:
        '''Initializes the DatabaseManager by connecting to the RDS database.'''
        load_dotenv()
        self.__connection = self._create_connection()

    def _create_connection(self) -> connection:
        '''Gets a connection to the RDS database'''
        return psycopg2.connect(
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USERNAME"],
            host=os.environ["DB_HOST"],
            password=os.environ["DB_PASSWORD"],
            port=os.environ["DB_PORT"],
        )

# GET METHODS
    def _get_frequent_topic(self, outlet: str) -> list[dict]:
        '''Retrieves the percentage that each topic has been covered by the given outlet'''
        with self.__connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(MOST_COVERED_TOPIC_QUERY,
                        (outlet, YESTERDAYS_DATE, outlet, YESTERDAYS_DATE))
            topic_frequency = cur.fetchall()
            return topic_frequency

    def _get_difference_in_topic(self) -> list[dict]:
        '''Retrieves the difference in average topic sentiment between outlets'''
        with self.__connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(SENTIMENT_BY_TOPIC_QUERY,
                        ('The Guardian', YESTERDAYS_DATE, 'Daily Express', YESTERDAYS_DATE))
            difference_in_topic = cur.fetchall()
        return difference_in_topic

    def _get_most_polarised_topics(self):
        '''Returns the top three most agreeable and polarised topics'''
        difference_in_topic = self._get_difference_in_topic()
        diff_topics = [topic.get('topic_name')
                       for topic in difference_in_topic[:3]]
        agree_topics = [topic.get('topic_name')
                        for topic in difference_in_topic[-3:]]
        return agree_topics, diff_topics

    def _get_outlet_sentiment(self, date_of_interest: date) -> dict[str:str]:
        '''Returns the average sentiment of each outlet for a given date'''
        with self.__connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(OUTLET_SENTIMENT_QUERY, (date_of_interest,))
            sentiment_score = cur.fetchall()
        return {score.get('news_outlet_name'): score.get('compound') for score in sentiment_score}

    def _get_difference_in_outlet(self) -> tuple[str:str]:
        '''Returns the average sentiment score for each day
          and whether this has changed since the previous day'''
        increase = '🟢⬆️'
        decrease = '🔴⬇️'
        equal = '🟡⏸️'
        express_change = equal
        guard_change = equal

        previous_date = (YESTERDAYS_DATE - timedelta(days=1)
                         ).strftime('%Y-%m-%d')
        yesterdays_sentiment_scores = self._get_outlet_sentiment(
            YESTERDAYS_DATE)
        two_days_sentiment_score = self._get_outlet_sentiment(previous_date)

        if yesterdays_sentiment_scores['The Guardian'] > two_days_sentiment_score['The Guardian']:
            guard_change = increase
        if yesterdays_sentiment_scores['The Guardian'] < two_days_sentiment_score['The Guardian']:
            guard_change = decrease
        if yesterdays_sentiment_scores['Daily Express'] > two_days_sentiment_score['Daily Express']:
            express_change = increase
        if yesterdays_sentiment_scores['Daily Express'] < two_days_sentiment_score['Daily Express']:
            express_change = decrease

        guardian_score = f"{yesterdays_sentiment_scores['The Guardian']} {guard_change}"
        express_score = f"{yesterdays_sentiment_scores['Daily Express']} {express_change}"

        return guardian_score, express_score

    def _get_main_image(self, article_url):
        '''Returns the image from the link provided'''
        article = Article(article_url)
        article.download()
        article.parse()
        return article.top_image

    def _combine_image_to_articles(self, articles: list[dict]) -> list[dict]:
        '''Adds an image to each article dictionary'''
        for article in articles:
            image = self._get_main_image(article.get('article_url'))
            article['image_url'] = image
        return articles

    def _get_top_polarising_articles(self, outlet: str) -> tuple[list[dict], list[dict]]:
        '''Finds the top polarising articles for the given outlet'''
        with self.__connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(TOP_NEGATIVE_ARTICLES,
                        (YESTERDAYS_DATE, outlet))
            positives = cur.fetchall()
            cur.execute(TOP_POSITIVE_ARTICLES,
                        (YESTERDAYS_DATE, outlet))
            negatives = cur.fetchall()

            positive_with_image = self._combine_image_to_articles(positives)
            negative_with_image = self._combine_image_to_articles(negatives)

            return positive_with_image, negative_with_image

    def _get_top_three_covered_topics(self) -> tuple[dict, dict]:
        '''Returns the top three covered topics for each outlet'''
        express_freq_topics = self._get_frequent_topic('Daily Express')
        guard_freq_topics = self._get_frequent_topic('The Guardian')

        guard_topics = [topic.get('topic_name')
                        for topic in guard_freq_topics[:3]]
        express_topics = [topic.get('topic_name')
                          for topic in express_freq_topics[:3]]
        return guard_topics, express_topics

    def _get_tilt_logo(self):
        '''Returns the decoded tilt logo png'''
        with open("tilt_logo.png", "rb") as img_file:
            base_image = b64encode(img_file.read()).decode('utf-8')
        return base_image

    def topics_sentiment_diff_bar_chart(self) -> list[str]:
        '''Returns a base64 encoded bar chart displaying
          the average topic sentiment for each outlet'''
        difference_in_topic = self._get_difference_in_topic()
        difference_in_topic_df = pd.DataFrame(difference_in_topic)
        fig = px.bar(difference_in_topic_df,
                     x='topic_name',
                     y=['guardian_compound', 'express_compound'],
                     title='Average Sentiment per Topic: Guardian vs Express',
                     labels={'topic_name': 'Topic',
                             'value': 'Average Sentiment Score'},
                     barmode='group',
                     color_discrete_map={'guardian_compound': 'red', 'express_compound': 'blue'})
        fig.update_layout(
            showlegend=True,
            width=700,
            title_x=0.5,
            height=450,
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": -0.8,
                "xanchor": "center",
                "x": 0.5,
                "font": {"size": 8}
            },)

        fig.write_image("/tmp/topics_compound.png")
        with open("/tmp/topics_compound.png", "rb") as img_file:
            base_image = b64encode(img_file.read()).decode('utf-8')
        return base_image

    def topics_freq_pie_chart(self, outlet: str) -> go.Figure:
        '''Returns a pie chart showing frequency of topics for the inputted outlet.'''
        difference_in_topic = self._get_frequent_topic(outlet)
        difference_in_topic_df = pd.DataFrame(difference_in_topic)
        pie_fig = px.pie(difference_in_topic_df, names='topic_name', values='topic_percentage',
                         title=f"Breakdown of topics covered by {outlet} yesterday")
        pie_fig.update_traces(
            textinfo='label+percent',
            insidetextorientation='radial',
            textposition='inside'
        )
        return pie_fig

    def combined_pie_charts(self) -> str:
        '''Returns a combined chart displaying pie charts for The Guardian and The Daily
        Express topics by coverage frequency'''
        specs = [[{'type': 'pie'}, {'type': 'pie'}]]
        fig = make_subplots(
            rows=1,
            cols=2,
            subplot_titles=("The Guardian", "Daily Express"),
            specs=specs
        )
        fig_guardian = self.topics_freq_pie_chart('The Guardian')
        fig_express = self.topics_freq_pie_chart('Daily Express')

        for trace in fig_guardian.data:
            fig.add_trace(trace, row=1, col=1)

        for trace in fig_express.data:
            fig.add_trace(trace, row=1, col=2)

        fig.update_layout(
            title_text="Topic Coverage per News Outlet",
            showlegend=False,
            width=700,
            title_x=0.5,
            height=450)

        fig.write_image("/tmp/combined_topics_freq.png")
        with open("/tmp/combined_topics_freq.png", "rb") as img_file:
            base_image = b64encode(img_file.read()).decode('utf-8')
        return base_image

    def generate_report_context(self):
        '''Returns the context required for the jinja environment'''
        # Get sentiment differences between outlets
        guard_score, express_score = self._get_difference_in_outlet()

        # Get most polarised and agreed-upon topics
        diff_topics, agree_topics = self._get_most_polarised_topics()
        guard_topics, express_topics = self._get_top_three_covered_topics()

        # Polarising articles
        guardian_pos_art, guardian_neg_art = self._get_top_polarising_articles(
            'The Guardian')
        express_pos_art, express_neg_art = self._get_top_polarising_articles(
            'Daily Express')

        # Generate charts (base64-encoded images)
        bar_chart = self.topics_sentiment_diff_bar_chart()
        combined_pie = self.combined_pie_charts()

        logo = self._get_tilt_logo()

        # Build the Jinja context dictionary
        context = {
            "YESTERDAYS_DATE": YESTERDAYS_DATE,
            "guard_score": guard_score,
            "express_score": express_score,
            "diff_topics": diff_topics,
            "agree_topics": agree_topics,
            "guard_topics": guard_topics,
            "express_topics": express_topics,
            "bar_chart": bar_chart,
            "combined_pie": combined_pie,
            "guardian_neg_art": guardian_neg_art,
            "guardian_pos_art": guardian_pos_art,
            "express_pos_art": express_pos_art,
            "express_neg_art": express_neg_art,
            "tilt_logo": logo}
        return context

    def generate_jinja_env(self):
        '''Generates an jinja2 environment and exports it to a html file'''
        jinja_env = Environment(loader=FileSystemLoader('template'))
        template = jinja_env.get_template('jinja_template.html')
        context = self.generate_report_context()
        rendered_html = template.render(context)
        with open('report.html', 'w', encoding='utf-8') as f:
            f.write(rendered_html)
        HTML('report.html').write_pdf('report.pdf')  # add /tmp/
        with open('report.pdf', "rb") as pdf_file:
            pdf = pdf_file.read()
        return pdf

    def raw_email_generator(self):
        '''Generates raw email content ready to be sent'''
        pdf_data = self.generate_jinja_env()
        from_email = "trainee.josh.allen@sigmalabs.co.uk"
        to_emails = [
            "trainee.antariksh.patel@sigmalabs.co.uk",
            "trainee.joseph.sasaki@sigmalabs.co.uk",
            "trainee.josh.allen@sigmalabs.co.uk",
            "trainee.jake.hussey@sigmalabs.co.uk"
        ]
        # Set up the MIME message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = ", ".join(to_emails)
        msg['Subject'] = f"TILT Sentiment Analysis Daily Report {YESTERDAYS_DATE}"

        # Email body
        body = MIMEText(
            f"""\
            <html>
                <body>
                    <p>Dear Customer,</p>

                    <p>
                        Please find attached your sentiment analysis summary report
                          for <strong>{YESTERDAYS_DATE}</strong>.
                        This report includes an overview of the key topics discussed
                          by The Guardian and Daily Express, overall sentiment trends, and notable changes compared to previous days.
                    </p>
                    <p>
                        Thank you for choosing our service.<br>
                        <br>
                        Best regards,<br>
                        The TILT Team
                    </p>
                </body>
            </html>
            """,
            'html'
        )

        msg.attach(body)
        part = MIMEApplication(pdf_data)
        part.add_header('Content-Disposition', 'attachment',
                        filename="document.pdf")
        msg.attach(part)
        return msg.as_bytes()

    def send_email(self):
        '''Sends the raw email to the target destinations'''
        raw_email_bytes = self.raw_email_generator()
        ses_client = boto3.client('ses', region_name='eu-west-2',
                                  aws_access_key_id=os.environ['ACCESS_KEY'],
                                  aws_secret_access_key=os.environ['SECRET_ACCESS_KEY'])

        response = ses_client.send_raw_email(
            RawMessage={
                'Data': raw_email_bytes
            },
            Source="trainee.antariksh.patel@sigmalabs.co.uk",
            Destinations=[
                # "trainee.antariksh.patel@sigmalabs.co.uk",
                # "trainee.joseph.sasaki@sigmalabs.co.uk",
                "trainee.josh.allen@sigmalabs.co.uk"
                # "trainee.jake.hussey@sigmalabs.co.uk"
            ])

        print("Email sent! Message ID:", response['MessageId'])

    def close_connection(self):
        '''Closes the database connection'''
        self.__connection.close()

 # pylint: disable=unused-argument
# pylint: disable=broad-exception-caught


def lambda_handler(event, context):
    '''Lambda function handler'''
    report = ReportCreator()
    try:
        report.generate_jinja_env()
        return {'statusCode': 200,
                'body': ' sent'}
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': f"Error sending email: {str(e)}"
        }

    finally:
        report.close_connection()


if __name__ == "__main__":
    print(lambda_handler([1, 2, 3], [1, 2, 3])
          )  # pylint: disable=unused-argument
