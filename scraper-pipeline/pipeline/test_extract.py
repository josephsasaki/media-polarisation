'''
    This file is responsible for testing the extract script
'''

from unittest.mock import patch, MagicMock
import pytest
import requests
from extract import GuardianRSSFeedExtractor, ExpressRSSFeedExtractor

# pylint: disable=redefined-outer-name, protected-access


@pytest.mark.parametrize("status_code, expected_output, expected_log", [
    (500, None, "Failed to retrieve the page. Status code: 500"),
    (403, None, "Failed to retrieve the page. Status code: 403"),
])
def test_body_extractor_success():
    """
    Test that _body_extractor returns parsed text when the request is successful (status code 200).
    """
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><p class='dcr-16w5gq9'>Test</p></html>"
        mock_get.return_value = mock_response

        extractor = GuardianRSSFeedExtractor(["http://mock.com/"])
        result = extractor._body_extractor("http://mock.com/")
        assert result == "Test"


@pytest.mark.parametrize("html, expected", [
    ("<html></html>", ""),
    ("<p class='dcr-16w5gq9'></p>", ""),
    ("<p class='dcr-16w5gq9'>   </p>", " "),
    ("<p class='wrong-class'>Should not be included</p>", ""),
])
def test_guardian_body_formatter_edge_cases(html, expected):
    """
    Test that the Guardian body formatter handles edge cases correctly,
    such as empty paragraphs, whitespace, or incorrect classes.
    """
    extractor = GuardianRSSFeedExtractor(["http://mock.com/"])
    result = extractor._body_formatter(html)
    assert result == expected


@pytest.mark.parametrize("html, expected", [
    ("<div class='text-description'><p></p></div>", ""),
    ("<div class='text-description'><p> </p></div>", " "),
    ("<div class='wrong-class'><p>Ignore me</p></div>", ""),
    ("<div class='text-description'></div>", ""),
])
def test_express_body_formatter_edge_cases(html, expected):
    """
    Test that the Express body formatter correctly handles HTML input,
    filtering out non-content elements and invalid structures.
    """
    extractor = ExpressRSSFeedExtractor(["http://mockexpress.com/"])
    result = extractor._body_formatter(html)
    assert result == expected


def test_body_extractor_timeout(capsys):
    """
    Test that _body_extractor handles request timeout exceptions gracefully
    and logs a timeout message.
    """
    with patch("requests.get", side_effect=requests.exceptions.Timeout):
        extractor = GuardianRSSFeedExtractor(["http://mock.com/"])
        result = extractor._body_extractor("http://mock.com/")

        captured = capsys.readouterr()
        assert result is None
        assert "Request to http://mock.com/ timed out." in captured.out


def test_body_extractor_request_exception(capsys):
    """
    Test that _body_extractor handles general request exceptions and logs an appropriate error.
    """
    with patch("requests.get", side_effect=requests.RequestException("Connection error")):
        extractor = GuardianRSSFeedExtractor(["http://mock.com/"])
        result = extractor._body_extractor("http://mock.com/")

        captured = capsys.readouterr()
        assert result is None
        assert "Request failed: Connection error" in captured.out


def test_rss_parser_skips_entries_with_no_url_or_body():
    """
    Test that the RSS parser skips entries that lack a valid URL or body content.
    """
    with patch("feedparser.parse") as mock_parse, \
            patch.object(GuardianRSSFeedExtractor, '_body_extractor', return_value=None):

        mock_parse.return_value.entries = [
            {'title': 'Title 1', 'link': None, 'published': 'Today'},
            {'title': 'Title 2', 'link': 'http://example.com/article2',
             'published': 'Today'}
        ]

        extractor = GuardianRSSFeedExtractor(["http://mockfeed.com/"])
        result = extractor._rss_parser("http://mockfeed.com/")
        assert not result


def test_rss_parser_returns_valid_article_dict():
    """
    Test that the RSS parser returns a structured dictionary for valid RSS entries.
    """
    with patch("feedparser.parse") as mock_parse, \
            patch.object(GuardianRSSFeedExtractor, '_body_extractor',
                         return_value="Article content"):

        mock_parse.return_value.entries = [{
            'title': 'Headline',
            'link': 'http://mock.com/article',
            'published': '2024-01-01'
        }]

        extractor = GuardianRSSFeedExtractor(["http://mockfeed.com/"])
        result = extractor._rss_parser("http://mockfeed.com/")
        assert result == [{
            'headline': 'Headline',
            'url': 'http://mock.com/article',
            'published_date': '2024-01-01',
            'news_outlet': 'The Guardian',
            'body': 'Article content'
        }]


def test_guardian_body_formatter_handles_multiple_paragraphs():
    """
    Test that the Guardian body formatter concatenates multiple paragraphs correctly.
    """
    html = '''
    <html><body>
        <p class="dcr-16w5gq9">Part 1.</p>
        <p class="dcr-16w5gq9">Part 2.</p>
    </body></html>
    '''
    extractor = GuardianRSSFeedExtractor(["url"])
    result = extractor._body_formatter(html)
    assert result == "Part 1.Part 2."


def test_get_news_outlet_guardian():
    """
    Test that the correct news outlet name is returned for Guardian extractor.
    """
    extractor = GuardianRSSFeedExtractor(["http://mock.com/"])
    result = extractor._get_news_outlet()
    assert result == "The Guardian"


def test_get_news_outlet_express():
    """
    Test that the correct news outlet name is returned for Express extractor.
    """
    extractor = ExpressRSSFeedExtractor(["http://mockexpress.com/"])
    result = extractor._get_news_outlet()
    assert result == "Daily Express"


def test_extract_feeds_combines_data_from_multiple_feeds():
    """
    Test that extract_feeds combines articles from multiple RSS feeds correctly.
    """
    with patch.object(GuardianRSSFeedExtractor, '_rss_parser', side_effect=[
        [{'headline': 'Article 1', 'url': 'http://mock.com/1', 'published_date': '2025-01-01',
          'news_outlet': 'The Guardian', 'body': 'Content 1'}],
        [{'headline': 'Article 2', 'url': 'http://mock.com/2',
          'published_date': '2025-01-02', 'news_outlet': 'The Guardian', 'body': 'Content 2'}]
    ]):
        extractor = GuardianRSSFeedExtractor(
            ["http://mockfeed1.com/", "http://mockfeed2.com/"])
        result = extractor.extract_feeds()
        assert len(result) == 2
        assert result[0]['headline'] == 'Article 1'
        assert result[1]['headline'] == 'Article 2'
        assert result[0]['body'] == 'Content 1'
        assert result[1]['body'] == 'Content 2'


def test_extract_feeds_with_empty_results():
    """
    Test that extract_feeds returns an empty list when no articles are parsed.
    """
    with patch.object(GuardianRSSFeedExtractor, '_rss_parser', side_effect=[
        [],
        []
    ]):
        extractor = GuardianRSSFeedExtractor(
            ["http://mockfeed1.com/", "http://mockfeed2.com/"])
        result = extractor.extract_feeds()
        assert not result


def test_body_extractor_failed_status_code(capsys):
    """
    Test that _body_extractor handles HTTP 404 errors and logs the correct message.
    """
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        extractor = GuardianRSSFeedExtractor(["http://mock.com/"])
        result = extractor._body_extractor("http://mock.com/")

        captured = capsys.readouterr()
        assert result is None
        assert "Failed to retrieve the page. Status code: 404" in captured.out


def test_body_extractor_success():
    """
    Duplicate: Test successful extraction and formatting of article body from Guardian.
    """
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><p class='dcr-16w5gq9'>Test</p></html>"
        mock_get.return_value = mock_response

        extractor = GuardianRSSFeedExtractor(["http://mock.com/"])
        result = extractor._body_extractor("http://mock.com/")
        assert result == "Test"


def test_body_extractor_non_200_status(capsys):
    """
    Duplicate: Test that non-200 responses are handled with logging and None return.
    """
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        extractor = GuardianRSSFeedExtractor(["http://mock.com/"])
        result = extractor._body_extractor("http://mock.com/")
        captured = capsys.readouterr()

        assert result is None
        assert "Failed to retrieve the page. Status code: 500" in captured.out


def test_body_extractor_empty_body():
    """
    Test that _body_extractor returns None if the article body is empty.
    """
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><p class='dcr-16w5gq9'></p></html>"
        mock_get.return_value = mock_response

        extractor = GuardianRSSFeedExtractor(["http://mock.com/"])
        result = extractor._body_extractor("http://mock.com/")

        assert result is None
