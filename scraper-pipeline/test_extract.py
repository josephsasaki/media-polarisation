from unittest.mock import patch, MagicMock

from extract import GuardianRSSFeedExtractor
import pytest


@pytest.fixture()
def success_request():
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.return_value = {"data": "valid response"}
        mock_get.return_value = mock_response

        yield mock_get


@pytest.fixture()
def failure_request():
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.return_value = None
        mock_get.return_value = mock_response

        yield mock_get


def test_guard_body_extractor_200(success_request):
    guard = GuardianRSSFeedExtractor(["http://mockcom/"])
    result = guard.body_extractor("http://mock.com/")
    assert result.return_value == {"data": "valid response"}


def test_express_body_extractor_200(success_request):
    guard = GuardianRSSFeedExtractor(["http://mockcom/"])
    result = guard.body_extractor("http://mock.com/")
    assert result.return_value == {"data": "valid response"}


def test_guard_body_extractor_404(failure_request, capsys):
    guard = GuardianRSSFeedExtractor(["http://mockcom/"])
    result = guard.body_extractor("http://mock.com/")
    captured = capsys.readouterr()
    assert result.return_value is None
    assert "No articles found." in captured.out


def test_express_body_extractor_404(failure_request, capsys):
    guard = GuardianRSSFeedExtractor(["http://mockcom/"])
    result = guard.body_extractor("http://mock.com/")
    captured = capsys.readouterr()
    assert result.return_value is None
    assert "No articles found." in captured.out
