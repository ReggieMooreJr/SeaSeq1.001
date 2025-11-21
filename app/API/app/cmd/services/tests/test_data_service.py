# ===============================
# Chapter 1: Unit Tests for data_service.py
# ===============================
import pytest
from app.services import data_service

def test_get_target_site_sets_and_gets(monkeypatch, tmp_path):
    monkeypatch.setattr(data_service, "DATA_DIR", tmp_path)
    url = "https://example.com"
    data_service.set_target_site(url)
    assert data_service.get_target_site() == url

def test_fetch_and_event_from_response(requests_mock):
    url = "https://example.com"
    html = "<html><body><a href='/a'></a><form><input type='password'></form></body></html>"
    requests_mock.get(url, text=html)
    _, response = data_service._fetch(url)
    event = data_service._event_from_response(url, response)
    assert event.page_url == url
    assert event.https is False or event.https is True
    assert event.num_links == 1
    assert event.num_forms == 1
    assert event.has_login_form is True
