'''This file is responsible for testing the extract script'''
from unittest.mock import patch, MagicMock
import requests
from extract import GuardianRSSFeedExtractor, ExpressRSSFeedExtractor, RSSFeedExtractor

# pylint: disable=protected-access


def test_body_extractor_200():
    '''Test _body_extractor returns response with valid status 200.'''
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.return_value = {"data": "valid response"}
        mock_get.return_value = mock_response

        guard = RSSFeedExtractor(["http://mockcom/"])
        result = guard._body_extractor("http://mock.com/")
        assert result.return_value == {"data": "valid response"}


def test_body_extractor_404(capsys):
    '''Test _body_extractor handles failed request with status 404 and prints error.'''
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.return_value = None
        mock_get.side_effect = requests.exceptions.RequestException(
            "Mock request failed")
        mock_get.return_value = mock_response

        guard = RSSFeedExtractor(["http://mockcom/"])
        result = guard._body_extractor("http://mock.com/")
        captured = capsys.readouterr()
        assert result is None
        assert "Request failed: Mock request failed" in captured.out


def test_body_extractor_timeout(capsys):
    '''Test _body_extractor handles timeout exception and prints timeout message.'''
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.return_value = None
        mock_get.side_effect = requests.exceptions.Timeout(
            "The request timed out")
        mock_get.return_value = mock_response

        guard = RSSFeedExtractor(["http://mockcom/"])
        result = guard._body_extractor("http://mock.com/")
        assert result is None
        captured = capsys.readouterr()
        assert "Request to http://mock.com/ timed out." in captured.out


def test_guardian_body_formatter_success():
    '''Test Guardian body_formatter returns correct text from valid HTML.'''
    html = '''
    <html>
        <body>
            <p class="dcr-16w5gq9">Paragraph 1.</p>
            <p class="dcr-16w5gq9">Paragraph 2.</p>
        </body>
    </html>
    '''
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = html

    extractor = GuardianRSSFeedExtractor(["http://mockfeed.com/"])
    result = extractor.body_formatter(mock_response)
    assert result == "Paragraph 1.Paragraph 2."


def test_guardian_body_formatter_empty_paragraphs():
    '''Test Guardian body_formatter returns None when no valid paragraphs exist.'''
    html = '<html><body><p class="some-other-class">Nothing here</p></body></html>'
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = html

    extractor = GuardianRSSFeedExtractor(["http://mockfeed.com/"])
    result = extractor.body_formatter(mock_response)
    assert result is None


def test_guardian_body_formatter_failed_status(capsys):
    '''Test Guardian body_formatter prints error and returns None on failed response.'''
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = ""

    extractor = GuardianRSSFeedExtractor(["http://mockfeed.com/"])
    result = extractor.body_formatter(mock_response)
    assert result is None

    captured = capsys.readouterr()
    assert "Failed to retrieve the page. Status code: 404" in captured.out


def test_express_body_formatter_success():
    '''Test Express body_formatter extracts paragraphs correctly from valid HTML.'''
    html = '''
    <html>
        <body>
            <div class="text-description">
                <p>Paragraph A.</p>
                <p>Paragraph B.</p>
            </div>
        </body>
    </html>
    '''
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = html

    extractor = ExpressRSSFeedExtractor(["http://mockexpress.com/"])
    result = extractor.body_formatter(mock_response)
    assert result == "Paragraph A.Paragraph B."


def test_express_body_formatter_no_matching_divs():
    '''Test Express body_formatter returns empty string when no matching divs are found.'''
    html = '<html><body><div class="other-class"><p>Nope</p></div></body></html>'
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = html

    extractor = ExpressRSSFeedExtractor(["http://mockexpress.com/"])
    result = extractor.body_formatter(mock_response)
    assert result == ""


def test_express_body_formatter_failed_status(capsys):
    '''Test Express body_formatter prints error and returns None on failed response.'''
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = ""

    extractor = ExpressRSSFeedExtractor(["http://mockexpress.com/"])
    result = extractor.body_formatter(mock_response)
    assert result is None

    captured = capsys.readouterr()
    assert "Failed to retrieve the page. Status code: 500" in captured.out


def test_rss_parser_with_valid_entries():
    '''Test _rss_parser processes valid feed entries and returns expected article body.'''
    mock_feed = MagicMock()
    mock_feed.entries = [{
        'title': 'Mock Title',
        'link': 'http://mock-article.com',
        'published': 'Mon, 01 Jan 2024 00:00:00 GMT'
    }]

    with patch("extract.feedparser.parse", return_value=mock_feed), \
            patch.object(RSSFeedExtractor, "_body_extractor", return_value="mock response"), \
            patch.object(RSSFeedExtractor, "body_formatter", return_value="Extracted content"):

        extractor = RSSFeedExtractor(["http://mock-feed.com"])
        result = extractor._rss_parser("http://mock-feed.com")

        assert isinstance(result, list)
        assert len(result) == 1
        article, body = result[0]
        assert article['title'] == 'Mock Title'
        assert article['link'] == 'http://mock-article.com'
        assert article['published'] == 'Mon, 01 Jan 2024 00:00:00 GMT'
        assert body == "Extracted content"


def test_rss_parser_with_no_entries(capsys):
    '''Test _rss_parser handles feed with no entries and prints appropriate message.'''
    mock_feed = MagicMock()
    mock_feed.entries = []

    with patch("extract.feedparser.parse", return_value=mock_feed):
        extractor = RSSFeedExtractor(["http://mock-feed.com"])
        result = extractor._rss_parser("http://mock-feed.com")

        assert result is None
        captured = capsys.readouterr()
        assert "No articles found." in captured.out


def test_rss_parser_skips_entry_without_body():
    '''Test _rss_parser skips feed entries with no extracted body content.'''
    mock_feed = MagicMock()
    mock_feed.entries = [{
        'title': 'Mock Title',
        'link': 'http://mock-article.com',
        'published': 'Mon, 01 Jan 2024 00:00:00 GMT'
    }]

    with patch("extract.feedparser.parse", return_value=mock_feed), \
            patch.object(RSSFeedExtractor, "_body_extractor", return_value="mock response"), \
            patch.object(RSSFeedExtractor, "body_formatter", return_value=None):

        extractor = RSSFeedExtractor(["http://mock-feed.com"])
        result = extractor._rss_parser("http://mock-feed.com")

        assert result == []


def test_extract_feeds_combines_results():
    '''Test extract_feeds combines parsed articles from multiple RSS URLs.'''
    mock_rss_data_1 = [("Article 1", "Body 1")]
    mock_rss_data_2 = [("Article 2", "Body 2")]

    feeds = ["http://mock-feed1.com", "http://mock-feed2.com"]
    extractor = RSSFeedExtractor(feeds)

    with patch.object(RSSFeedExtractor, "_rss_parser", side_effect=[mock_rss_data_1,
                                                                    mock_rss_data_2]):
        combined = extractor.extract_feeds()

        assert combined == mock_rss_data_1 + mock_rss_data_2
