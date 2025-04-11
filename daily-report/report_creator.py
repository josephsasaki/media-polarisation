'''
Script for extracting insights from the rds and writing them up into a report
'''
import os
from datetime import date
from dotenv import load_dotenv
import plotly.express as px
import pandas as pd
import psycopg2.extras
from psycopg2.extensions import connection
from base64 import b64encode
import plotly.graph_objects as go
from plotly.subplots import make_subplots


SENTIMENT_BY_TOPIC_QUERY = '''
                WITH guardian_topics_avg AS (SELECT t.topic_name,
                    AVG(at.article_topic_compound_sentiment::numeric) AS compound
                    FROM article_topic as at
                    JOIN topic AS t ON t.topic_id = at.topic_id
                    JOIN article AS a ON a.article_id = at.article_id
                    JOIN news_outlet AS no ON no.news_outlet_id = a.news_outlet_id
                    WHERE no.news_outlet_name = %s
                    GROUP BY t.topic_name),

                express_topics_avg AS (SELECT t.topic_name,
                    AVG(at.article_topic_compound_sentiment::numeric) AS compound
                    FROM article_topic as at
                    JOIN topic AS t ON t.topic_id = at.topic_id
                    JOIN article AS a ON a.article_id = at.article_id
                    JOIN news_outlet AS no ON no.news_outlet_id = a.news_outlet_id
                    WHERE no.news_outlet_name = %s
                    GROUP BY t.topic_name)

                    SELECT gta.topic_name, ROUND(gta.compound, 2):: float AS guardian_compound, ROUND(eta.compound, 2):: float AS express_compound, ROUND(ABS(gta.compound - eta.compound),2)::float AS compound_diff
                    FROM guardian_topics_avg gta
                    INNER JOIN express_topics_avg eta ON eta.topic_name = gta.topic_name
                    ORDER BY compound_diff DESC
                    ;'''

#    AVG(at.article_topic_positive_sentiment: : numeric) AS positive,
#             AVG(at.article_topic_negative_sentiment: : numeric) AS negative,
#             AVG(at.article_topic_neutral_sentiment: : numeric) AS neutral,

# ROUND(ABS(gta.positive - eta.positive), 2) AS positive_diff,
# ROUND(ABS(gta.negative - eta.negative), 2) AS negative_diff,
# ROUND(ABS(gta.neutral - eta.neutral), 2) AS neutral_diff,
# AND a.article_published_date: : DATE = %s

MOST_COVERED_TOPIC_QUERY = '''WITH topic_counts AS (
    SELECT t.topic_name, COUNT(*) AS topic_frequency
    FROM article_topic AS at
    JOIN topic AS t ON t.topic_id = at.topic_id
    JOIN article AS a ON a.article_id = at.article_id
    JOIN news_outlet AS no ON no.news_outlet_id = a.news_outlet_id
    WHERE no.news_outlet_name = %s
    GROUP BY t.topic_name
),
total_topics AS (
    SELECT COUNT(*) AS total_count
    FROM article_topic AS at
    JOIN article AS a ON a.article_id = at.article_id
    JOIN news_outlet AS no ON no.news_outlet_id = a.news_outlet_id
    WHERE no.news_outlet_name = %s
)

SELECT tc.topic_name,
       ROUND((tc.topic_frequency * 100.0) / tt.total_count, 2) AS topic_percentage
FROM topic_counts tc
JOIN total_topics tt ON true
ORDER BY topic_percentage DESC;
'''


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

    def _get_guardian_frequent_topic(self):
        '''Retrieves the average topic sentiments for each outlet'''
        with self.__connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(MOST_COVERED_TOPIC_QUERY,
                        ('The Guardian', 'The Guardian'))
            topic_frequency = cur.fetchall()
            return topic_frequency

    def _get_express_frequent_topic(self):
        '''Retrieves the average topic sentiments for each outlet'''
        with self.__connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(MOST_COVERED_TOPIC_QUERY,
                        ('Daily Express', 'Daily Express'))
            topic_frequency = cur.fetchall()
            print(topic_frequency)
        return topic_frequency

    def _get_difference_in_topic(self):
        '''Retrieves the average topic sentiments for each outlet and the difference between outlets'''
        with self.__connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            date_now = date.today()
            cur.execute(SENTIMENT_BY_TOPIC_QUERY,
                        ('The Guardian', 'Daily Express'))
            difference_in_topic = cur.fetchall()

        return difference_in_topic

    def topics_sentiment_diff_bar_chart(self) -> list[str]:
        '''Returns a bar chart displaying the average topic compound sentiment for each outlet'''
        difference_in_topic = self._get_difference_in_topic()
        difference_in_topic_df = pd.DataFrame(difference_in_topic)

        print(difference_in_topic_df)

        fig = px.bar(difference_in_topic_df,
                     x='topic_name',
                     y=['guardian_compound', 'express_compound'],
                     title='Sentiment Comparison: Guardian vs Express',
                     labels={'topic_name': 'Topic',
                             'value': 'Compound Sentiment'},
                     barmode='group',
                     color_discrete_map={'guardian_compound': 'red', 'express_compound': 'blue'})
        fig.update_layout(
            title_text="Topic Breakdown: The Guardian vs The Daily Express",
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

    def guardian_topics_freq_bar_chart(self) -> go.Figure:
        '''Returns a pie chart for The Guardian showing frequent topics.'''
        difference_in_topic = self._get_guardian_frequent_topic()
        difference_in_topic_df = pd.DataFrame(difference_in_topic)

        # Create the pie chart for The Guardian
        fig_guardian = px.pie(difference_in_topic_df, names='topic_name', values='topic_percentage',
                              title="Breakdown of topics covered by The Guardian yesterday")

        return fig_guardian

    def express_topics_freq_bar_chart(self) -> go.Figure:
        '''Returns a pie chart for The Daily Express showing frequent topics.'''
        difference_in_topic = self._get_express_frequent_topic()
        difference_in_topic_df = pd.DataFrame(difference_in_topic)

        # Create the pie chart for The Daily Express
        fig_express = px.pie(difference_in_topic_df, names='topic_name', values='topic_percentage',
                             title="Breakdown of topics covered by The Daily Express yesterday")

        return fig_express

    def combined_pie_charts(self) -> str:
        '''Returns a combined bar chart displaying pie charts for The Guardian and The Daily Express'''
        # Create a subplot layout (2 columns, 1 row)
    # Define specs to indicate that the subplots should be pie charts
        specs = [[{'type': 'pie'}, {'type': 'pie'}]]

        # Create subplots with the defined specs for pie charts
        fig = make_subplots(
            rows=1,
            cols=2,
            subplot_titles=("The Guardian", "The Daily Express"),
            specs=specs  # Specify that both subplots are for pie charts
        )

        # Get both pie charts
        fig_guardian = self.guardian_topics_freq_bar_chart()
        fig_express = self.express_topics_freq_bar_chart()

        # Add the pie chart data to the subplots
        for trace in fig_guardian.data:
            fig.add_trace(trace, row=1, col=1)

        for trace in fig_express.data:
            fig.add_trace(trace, row=1, col=2)

        # Update layout to adjust spacing and appearance
        fig.update_layout(
            title_text="Topic Breakdown: The Guardian vs The Daily Express",
            showlegend=True,
            height=580,  # Increase the height of the entire figure
            width=1000,
            title_x=0.5,
            legend=dict(
                orientation="h",  # Horizontal legend
                yanchor="bottom",  # Align legend to the bottom
                y=-0.3,  # Place the legend below the chart
                xanchor="center",  # Center the legend horizontally
                x=0.5,
                font=dict(
                    size=8)  # Center the legend horizontally
            ),
        )

        # Write image to file
        fig.write_image("combined_topics_freq.png")
        with open("combined_topics_freq.png", "rb") as img_file:
            base_image = b64encode(img_file.read()).decode('utf-8')
        return base_image

    def write_to_html(self):
        """Writes analysis to html"""
        today_date = date.today()
        bar_chart = self.topics_sentiment_diff_bar_chart()
        polarised_topics = self._get_difference_in_topic()
        diff_topics = [topic.get('topic_name')
                       for topic in polarised_topics[:3]]
        agree_topics = [topic.get('topic_name')
                        for topic in polarised_topics[-3:]]
        express_freq_topics = self._get_express_frequent_topic()
        guard_freq_topics = self._get_guardian_frequent_topic()

        guard_topics = [topic.get('topic_name')
                        for topic in guard_freq_topics[:3]]
        express_topics = [topic.get('topic_name')
                          for topic in express_freq_topics[:3]]

        combined_pie = self.combined_pie_charts()

        html_string = f"""
                            <html>
                            <head>
                                <style>
                                    html, body {{
                                        margin: 0;
                                        padding: 0;
                                        height: 100%;
                                        width: 100%;
                                        font-family: Arial, sans-serif;
                                        text-align: center;
                                        background-color: #f9f9f9;
                                    }}
                                    .container {{
                                        width: 100%;
                                        max-width: 1200px;
                                        margin: auto;
                                        padding: 20px;
                                    }}
                                    h1, h2 {{
                                        color: #333;
                                    }}

                                </style>
                            </head>
                            <body>
                                <div class="container">
                                    <h1>News Polarisation Analysis {today_date}</h1>
                                    <br>
                                    <h2>Most Polarised Topics Today</h2>
                                    <p>Today's news coverage from two prominent UK outlets—the left-leaning
                                    <em>Guardian</em> and the right-leaning <em>Daily Express</em>—has been analyzed
                                      for potential bias. The analysis revealed significant disparities in perspective
                                        on the following topics: <strong>{diff_topics[0]}</strong>, <strong>{diff_topics[1]}</strong>,
                                          and <strong>{diff_topics[2]}</strong>. Conversely, the following topics were found to have
                                            the most agreement between the two sources: <strong>{agree_topics[0]}</strong>, <strong>{agree_topics[1]}</strong>, <strong>{agree_topics[2]}</strong>.</p>
                                    <br>
                                    <img src="data:image/png;base64,{bar_chart}" alt="Polarisation Chart"/>
                                    <br>
                                    <br>
                                    <h2>Topic Coverage</h2>
                                    <p>Both Newspaper Outlets covered a broad range of topics in their news coverage, with the <strong>{guard_topics[0]}</strong>,
                                    <strong>{guard_topics[1]}</strong>, <strong>{guard_topics[2]}</strong>
                                    being covered most frequently for The Guardian and <strong>{express_topics[0]}</strong>, <strong>{express_topics[1]}</strong>,
                                    <strong>{express_topics[2]}</strong> being covered most frequently for the Daily Express</p>
                                    <br>
                                    <img src="data:image/png;base64,{combined_pie}" alt="Polarisation Chart" style="width: 100%;">



                                </div>
                            </body>
                            </html>
                            """

        with open("report.html", "w") as file:
            file.write(html_string)

    def close_connection(self):
        '''Closes the database connection'''
        self.__connection.close()


if __name__ == "__main__":
    report = ReportCreator()
    try:
        report.write_to_html()
    finally:
        report.close_connection()
