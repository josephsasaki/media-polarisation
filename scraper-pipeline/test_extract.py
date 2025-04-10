'''
    This file is responsible for testing the extract script
'''

from unittest.mock import patch, MagicMock
import requests
from extract import GuardianRSSFeedExtractor, ExpressRSSFeedExtractor

# pylint: disable=protected-access


def test_body_extractor_200():
    '''Test _body_extractor returns response with valid status 200.'''
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><p class='dcr-16w5gq9'>Test</p></html>"
        mock_get.return_value = mock_response

        guard = GuardianRSSFeedExtractor(["http://mock.com/"])
        result = guard._body_extractor("http://mock.com/")
        assert result == "Test"


def test_body_extractor_404(capsys):
    '''Test _body_extractor handles failed request with status 404 and prints error.'''
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        guard = GuardianRSSFeedExtractor(["http://mock.com/"])
        result = guard._body_extractor("http://mock.com/")
        captured = capsys.readouterr()
        assert result is None
        assert "Failed to retrieve the page. Status code: 404" in captured.out


def test_body_extractor_timeout(capsys):
    '''Test _body_extractor handles timeout exception and prints timeout message.'''
    with patch("requests.get", side_effect=requests.exceptions.Timeout):
        guard = GuardianRSSFeedExtractor(["http://mock.com/"])
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
    extractor = GuardianRSSFeedExtractor(["http://mockfeed.com/"])
    result = extractor._body_formatter(html)
    assert result == "Paragraph 1.Paragraph 2."


def test_guardian_body_formatter_empty_paragraphs():
    '''Test Guardian body_formatter returns empty string when no valid paragraphs exist.'''
    html = '<html><body><p class="some-other-class">Nothing here</p></body></html>'
    extractor = GuardianRSSFeedExtractor(["http://mockfeed.com/"])
    result = extractor._body_formatter(html)
    assert result == ""


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
    extractor = ExpressRSSFeedExtractor(["http://mockexpress.com/"])
    result = extractor._body_formatter(html)
    assert result == "Paragraph A.Paragraph B."


def test_express_body_formatter_no_matching_divs():
    '''Test Express body_formatter returns empty string when no matching divs are found.'''
    html = '<html><body><div class="other-class"><p>Nope</p></div></body></html>'
    extractor = ExpressRSSFeedExtractor(["http://mockexpress.com/"])
    result = extractor._body_formatter(html)
    assert result == ""


def test_extract_guardian_get_news_outlet():
    '''Finds the news outlet for the Guardian extractor'''
    assert GuardianRSSFeedExtractor(
        ["test/feed"])._get_news_outlet() == "The Guardian"


def test_extract_express_get_news_outlet():
    '''Finds the news outlet for the Express extractor'''
    assert ExpressRSSFeedExtractor(
        ["test/feed"])._get_news_outlet() == "Daily Express"
