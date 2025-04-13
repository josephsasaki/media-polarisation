'''
Script for extracting insights from the rds and writing them up into a report
'''
import os
from datetime import date, timedelta
from dotenv import load_dotenv
import plotly.express as px
import pandas as pd
import psycopg2.extras
from psycopg2.extensions import connection
from base64 import b64encode
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from jinja2 import Environment, FileSystemLoader, Template
from xhtml2pdf import pisa


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
    def _get_frequent_topic(self, outlet):
        '''Retrieves the average topic sentiments for each outlet'''
        with self.__connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(MOST_COVERED_TOPIC_QUERY,
                        (outlet, YESTERDAYS_DATE, outlet, YESTERDAYS_DATE))
            topic_frequency = cur.fetchall()
            return topic_frequency

    def _get_difference_in_topic(self):
        '''Retrieves the average topic sentiments for each outlet and the difference between outlets'''
        with self.__connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            date_now = date.today()
            cur.execute(SENTIMENT_BY_TOPIC_QUERY,
                        ('The Guardian', YESTERDAYS_DATE, 'Daily Express', YESTERDAYS_DATE))
            difference_in_topic = cur.fetchall()

        return difference_in_topic

    def _get_difference_in_outlet(self):
        '''Retrieves the average topic sentiment between different between outlets'''
        with self.__connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            previous_date = (YESTERDAYS_DATE -
                             timedelta(days=1)).strftime('%Y-%m-%d')
            cur.execute(OUTLET_SENTIMENT_QUERY, (YESTERDAYS_DATE,))
            yesterdays_scores = cur.fetchall()
            cur.execute(OUTLET_SENTIMENT_QUERY, (previous_date, ))
            two_days_scores = cur.fetchall()
            yesterdays_scores_tool = {
                score.get('news_outlet_name'): score.get('compound') for score in yesterdays_scores}
            two_days_scores_tool = {
                score.get('news_outlet_name'): score.get('compound') for score in two_days_scores}

            increase = '🟢⬆️'
            decrease = '🔴⬇️'

            express = decrease
            guard = decrease

            if yesterdays_scores_tool['The Guardian'] > two_days_scores_tool['The Guardian']:
                guard = increase
            if yesterdays_scores_tool['Daily Express'] > two_days_scores_tool['Daily Express']:
                express = increase

            return f"{yesterdays_scores_tool['The Guardian']} {guard}", f"{yesterdays_scores_tool['Daily Express']} {express}"

    def guard_articles(self):
        '''Finds the top polarising articles for the guardian'''
        with self.__connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(TOP_NEGATIVE_ARTICLES,
                        (YESTERDAYS_DATE, 'The Guardian'))
            guardian_positives = cur.fetchall()
            cur.execute(TOP_POSITIVE_ARTICLES,
                        (YESTERDAYS_DATE, 'The Guardian'))
            guardian_negatives = cur.fetchall()
            return guardian_positives, guardian_negatives

    def express_articles(self):
        '''Finds the top polarising articles for daily express'''
        with self.__connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(TOP_NEGATIVE_ARTICLES,
                        (YESTERDAYS_DATE, 'Daily Express'))
            express_positives = cur.fetchall()
            cur.execute(TOP_POSITIVE_ARTICLES,
                        (YESTERDAYS_DATE, 'Daily Express'))
            express_negatives = cur.fetchall()
            return express_positives, express_negatives


# GRAPH METHODS

    def topics_sentiment_diff_bar_chart(self) -> list[str]:
        '''Returns a bar chart displaying the average topic compound sentiment for each outlet'''
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
            height=500,  # Increase the height of the entire figure
            width=1000,
            title_x=0.5,
            legend=dict(
                orientation="h",  # Horizontal legend
                yanchor="bottom",  # Align legend to the bottom
                y=-0.5,  # Place the legend below the chart
                xanchor="center",  # Center the legend horizontally
                x=0.5,
                font=dict(
                    size=8)  # Center the legend horizontally
            ),)

        fig.write_image("topics_compound.png")
        with open("topics_compound.png", "rb") as img_file:
            base_image = b64encode(img_file.read()).decode('utf-8')
        return base_image

    def guardian_topics_freq_pie_chart(self) -> go.Figure:
        '''Returns a pie chart for The Guardian showing frequent topics.'''
        difference_in_topic = self._get_frequent_topic('The Guardian')
        difference_in_topic_df = pd.DataFrame(difference_in_topic)

        fig_guardian = px.pie(difference_in_topic_df, names='topic_name', values='topic_percentage',
                              title="Breakdown of topics covered by The Guardian yesterday")

        fig_guardian.update_traces(
            textinfo='label+percent',   # Shows only label and percent
            insidetextorientation='radial',
            textposition='inside'
        )

        return fig_guardian

    def express_topics_freq_pie_chart(self) -> go.Figure:
        '''Returns a pie chart for The Daily Express showing frequent topics.'''
        difference_in_topic = self._get_frequent_topic('Daily Express')
        difference_in_topic_df = pd.DataFrame(difference_in_topic)

        fig_express = px.pie(difference_in_topic_df, names='topic_name', values='topic_percentage',
                             title="Breakdown of topics covered by The Daily Express yesterday")

        fig_express.update_traces(
            textinfo='label+percent',   # Shows only label and percent
            insidetextorientation='radial',
            textposition='inside'
        )

        return fig_express

    def combined_pie_charts(self) -> str:
        '''Returns a combined bar chart displaying pie charts for The Guardian and The Daily Express'''
        # Create a subplot layout (2 columns, 1 row)

        specs = [[{'type': 'pie'}, {'type': 'pie'}]]

        fig = make_subplots(
            rows=1,
            cols=2,
            subplot_titles=("The Guardian", "Daily Express"),
            specs=specs
        )

        fig_guardian = self.guardian_topics_freq_pie_chart()
        fig_express = self.express_topics_freq_pie_chart()

        for trace in fig_guardian.data:
            fig.add_trace(trace, row=1, col=1)

        for trace in fig_express.data:
            fig.add_trace(trace, row=1, col=2)

        # Update layout to adjust spacing and appearance
        fig.update_layout(
            title_text="Topic Coverage per News Outlet",
            showlegend=True,
            height=400,
            width=750,
            title_x=0.5,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.6,
                xanchor="center",
                x=0.5,
                font=dict(
                    size=6)
            ),
        )

        fig.write_image("combined_topics_freq.png")
        with open("combined_topics_freq.png", "rb") as img_file:
            base_image = b64encode(img_file.read()).decode('utf-8')
        return base_image

    def generate_report_context(self):
        # Needs refactoring
        # Get sentiment differences between outlets
        guard_score, express_score = self._get_difference_in_outlet()

        # Get most polarised and agreed-upon topics
        polarised_topics = self._get_difference_in_topic()
        diff_topics = [topic.get('topic_name')
                       for topic in polarised_topics[:3]]
        agree_topics = [topic.get('topic_name')
                        for topic in polarised_topics[-3:]]

        # Get most frequently covered topics for each outlet
        express_freq_topics = self._get_frequent_topic('Daily Express')
        guard_freq_topics = self._get_frequent_topic('The Guardian')

        guard_topics = [topic.get('topic_name')
                        for topic in guard_freq_topics[:3]]
        express_topics = [topic.get('topic_name')
                          for topic in express_freq_topics[:3]]

        # Polarising articles
        guardian_pos_art, guardian_neg_art = self.guard_articles()
        express_pos_art, express_neg_art = self.express_articles()

        # Generate charts (base64-encoded images)
        bar_chart = self.topics_sentiment_diff_bar_chart()
        combined_pie = self.combined_pie_charts()

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
            "express_neg_art": express_neg_art


        }
        return context

    def generate_jinja_env(self):
        '''Generates an jinja2 environment and exports it to a html file'''
        jinja_env = Environment(loader=FileSystemLoader('template'))
        template = jinja_env.get_template('report.html')
        context = self.generate_report_context()
        rendered_html = template.render(context)
        with open('output.html', 'w') as f:
            f.write(rendered_html)

    def close_connection(self):
        '''Closes the database connection'''
        self.__connection.close()


if __name__ == "__main__":
    report = ReportCreator()
    try:
        report.generate_jinja_env()

    finally:
        report.close_connection()
