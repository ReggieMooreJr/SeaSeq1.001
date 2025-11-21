# ===============================
# Chapter 1: Unit Tests for learning_service.py
# ===============================
import pytest
import numpy as np
from app.services import learning_service
from app.models.events import SecurityEvent

def make_events():
    return [
        SecurityEvent(page_url="http://a.com", https=True, num_links=5, num_forms=1, has_login_form=False, headers={}),
        SecurityEvent(page_url="http://b.com", https=False, num_links=2, num_forms=0, has_login_form=True, headers={}),
    ]

def test_featurize():
    events = make_events()
    X = learning_service._featurize(events)
    assert isinstance(X, np.ndarray)
    assert X.shape[1] == 4

def test_train_and_score(tmp_path, monkeypatch):
    monkeypatch.setattr(learning_service, "MODEL_DIR", tmp_path)
    monkeypatch.setattr(learning_service, "MODEL_PATH", tmp_path / "isoforest.pkl")
    events = make_events() * 10
    result = learning_service.train(events)
    assert result.trained_on == 20
    scores = learning_service.score(events)
    assert len(scores) == 20
    assert np.all(scores >= 0) and np.all(scores <= 1)
