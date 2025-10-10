import pytest
from workers.tasks import calculate_news_value
from core.config import Settings

# Use a dedicated test settings instance to avoid side-effects
test_settings = Settings(
    HIGH_IMPACT_KEYWORDS=["kaza", "patlama"],
    KEYWORD_WEIGHT=0.4,
    SOURCE_AUTHORITY_WEIGHT=0.2,
    SOCIAL_VELOCITY_WEIGHT=0.3,
    SENTIMENT_INTENSITY_WEIGHT=0.1
)

def test_calculate_news_value_high_score():
    """
    Test a scenario where a high score is expected due to multiple factors.
    """
    intel_item = {
        "headline": "Son dakika! Büyük bir kaza oldu.",
        "summary": "Şehir merkezinde bir patlama ve kaza meydana geldi.",
        "authority_tier": 5, # High authority source
        "sentiment_score": -0.8 # Strong negative sentiment
    }
    x_trends = ["kaza", "sondakika"] # Trending keyword

    # Temporarily override the global settings for the duration of the test
    from workers import tasks
    original_settings = tasks.settings
    tasks.settings = test_settings

    score = calculate_news_value(intel_item, x_trends)

    # Revert settings to avoid side-effects
    tasks.settings = original_settings

    # Let's break down the expected score:
    # Keyword score: "kaza", "patlama" found. 2 * 2.5 = 5.0. -> 5.0 * 0.4 = 2.0
    # Authority score: Tier 5 -> 5 * 2 = 10.0. -> 10.0 * 0.2 = 2.0
    # Social Velocity: "kaza" is trending. -> 10.0 * 0.3 = 3.0
    # Sentiment score: |-0.8| * 10 = 8.0. -> 8.0 * 0.1 = 0.8
    # Total = 2.0 + 2.0 + 3.0 + 0.8 = 7.8, which rounds to 8.
    assert score == 8

def test_calculate_news_value_low_score():
    """
    Test a scenario where a low score is expected.
    """
    intel_item = {
        "headline": "Güneşli bir gün",
        "summary": "Bugün hava çok güzel.",
        "authority_tier": 1, # Low authority
        "sentiment_score": 0.1 # Neutral sentiment
    }
    x_trends = ["finans", "politika"] # Not trending

    from workers import tasks
    original_settings = tasks.settings
    tasks.settings = test_settings

    score = calculate_news_value(intel_item, x_trends)

    tasks.settings = original_settings

    # Keyword score: 0 found -> 0.0 * 0.4 = 0.0
    # Authority score: Tier 1 -> 1 * 2 = 2.0 -> 2.0 * 0.2 = 0.4
    # Social Velocity: Not trending -> 2.0 * 0.3 = 0.6
    # Sentiment score: |0.1| * 10 = 1.0 -> 1.0 * 0.1 = 0.1
    # Total = 0.0 + 0.4 + 0.6 + 0.1 = 1.1, which rounds to 1.
    assert score == 1