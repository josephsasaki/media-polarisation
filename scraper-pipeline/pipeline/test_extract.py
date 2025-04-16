'''
    This file is responsible for testing the extract script
'''

from unittest.mock import patch
import pytest
from unittest.mock import patch, MagicMock
import requests
from extract import GuardianRSSFeedExtractor, ExpressRSSFeedExtractor


@pytest.mark.parametrize("status_code, expected_output, expected_log", [
    (500, None, "Failed to retrieve the page. Status code: 500"),
    (403, None, "Failed to retrieve the page. Status code: 403"),
])
def test_body_extractor_non_200_status(capsys, status_code, expected_output, expected_log):
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_get.return_value = mock_response

        guard = GuardianRSSFeedExtractor(["http://mock.com/"])
        result = guard._body_extractor("http://mock.com/")
        captured = capsys.readouterr()
        assert result == expected_output
        assert expected_log in captured.out


@pytest.mark.parametrize("html, expected", [
    ("<html></html>", ""),
    ("<p class='dcr-16w5gq9'></p>", ""),
    ("<p class='dcr-16w5gq9'>   </p>", " "),
    ("<p class='wrong-class'>Should not be included</p>", ""),
])
def test_guardian_body_formatter_edge_cases(html, expected):
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
    extractor = ExpressRSSFeedExtractor(["http://mockexpress.com/"])
    result = extractor._body_formatter(html)
    assert result == expected


def test_body_extractor_success():
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><p class='dcr-16w5gq9'>Test</p></html>"
        mock_get.return_value = mock_response

        extractor = GuardianRSSFeedExtractor(["http://mock.com/"])
        result = extractor._body_extractor("http://mock.com/")
        assert result == "Test"


def test_body_extractor_timeout(capsys):
    with patch("requests.get", side_effect=requests.exceptions.Timeout):
        extractor = GuardianRSSFeedExtractor(["http://mock.com/"])
        result = extractor._body_extractor("http://mock.com/")

        captured = capsys.readouterr()
        assert result is None
        assert "Request to http://mock.com/ timed out." in captured.out


def test_body_extractor_request_exception(capsys):
    with patch("requests.get", side_effect=requests.RequestException("Connection error")):
        extractor = GuardianRSSFeedExtractor(["http://mock.com/"])
        result = extractor._body_extractor("http://mock.com/")

        captured = capsys.readouterr()
        assert result is None
        assert "Request failed: Connection error" in captured.out


def test_rss_parser_skips_entries_with_no_url_or_body():
    with patch("feedparser.parse") as mock_parse, \
            patch.object(GuardianRSSFeedExtractor, '_body_extractor', return_value=None):

        mock_parse.return_value.entries = [
            {'title': 'Title 1', 'link': None, 'published': 'Today'},
            {'title': 'Title 2', 'link': 'http://example.com/article2',
                'published': 'Today'}
        ]

        extractor = GuardianRSSFeedExtractor(["http://mockfeed.com/"])
        result = extractor._rss_parser("http://mockfeed.com/")
        assert result == []


def test_rss_parser_returns_valid_article_dict():
    with patch("feedparser.parse") as mock_parse, \
            patch.object(GuardianRSSFeedExtractor, '_body_extractor', return_value="Article content"):

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
    extractor = GuardianRSSFeedExtractor(["http://mock.com/"])
    result = extractor._get_news_outlet()
    assert result == "The Guardian"


def test_get_news_outlet_express():
    extractor = ExpressRSSFeedExtractor(["http://mockexpress.com/"])
    result = extractor._get_news_outlet()
    assert result == "Daily Express"


def test_extract_feeds_combines_data_from_multiple_feeds():
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
    with patch.object(GuardianRSSFeedExtractor, '_rss_parser', side_effect=[
        [],
        []
    ]):
        extractor = GuardianRSSFeedExtractor(
            ["http://mockfeed1.com/", "http://mockfeed2.com/"])
        result = extractor.extract_feeds()
        assert result == []


def test_body_extractor_failed_status_code(capsys):
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
    with patch("requests.get") as mock_get:
        # Mock the response object
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><p class='dcr-16w5gq9'>Test</p></html>"
        mock_get.return_value = mock_response

        # Create the extractor object (assuming GuardianRSSFeedExtractor is defined)
        extractor = GuardianRSSFeedExtractor(["http://mock.com/"])
        result = extractor._body_extractor("http://mock.com/")

        # Ensure the result is the text body formatted
        assert result == "Test"


def test_body_extractor_non_200_status(capsys):
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        extractor = GuardianRSSFeedExtractor(["http://mock.com/"])
        result = extractor._body_extractor("http://mock.com/")
        captured = capsys.readouterr()

        # Assert that None is returned and the correct error message is printed
        assert result is None
        assert "Failed to retrieve the page. Status code: 500" in captured.out


def test_body_extractor_empty_body():
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><p class='dcr-16w5gq9'></p></html>"  # Empty content
        mock_get.return_value = mock_response

        extractor = GuardianRSSFeedExtractor(["http://mock.com/"])
        result = extractor._body_extractor("http://mock.com/")

        # Assert that None is returned due to an empty body
        assert result is None


def test_body_extractor_timeout(capsys):
    with patch("requests.get", side_effect=requests.exceptions.Timeout):
        extractor = GuardianRSSFeedExtractor(["http://mock.com/"])
        result = extractor._body_extractor("http://mock.com/")

        captured = capsys.readouterr()
        # Assert that None is returned and the timeout message is printed
        assert result is None
        assert "Request to http://mock.com/ timed out." in captured.out


def test_body_extractor_request_exception(capsys):
    with patch("requests.get", side_effect=requests.RequestException("Connection error")):
        extractor = GuardianRSSFeedExtractor(["http://mock.com/"])
        result = extractor._body_extractor("http://mock.com/")

        captured = capsys.readouterr()
        # Assert that None is returned and the exception message is printed
        assert result is None
        assert "Request failed: Connection error" in captured.out
