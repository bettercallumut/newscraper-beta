import celery
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

# Assuming core.config and core.models are in the python path.
# This will be true when running via the project's entry points.
from core.config import settings
from core.models import NewsBriefing

# --- Mocks & Placeholders for External Dependencies ---

def get_x_trends_for_turkey() -> List[str]:
    """
    Placeholder for a function that scrapes or APIs into X trends.
    In a real implementation, this would involve a robust scraper or API client.
    """
    print("Fetching mock X trends for Turkey...")
    # Returning common, high-impact Turkish news keywords
    return ["ekonomik kriz", "yeni vergi", "sondakika", "kabine toplantısı", "merkez bankası"]

def call_gemini_for_analysis(raw_intel: Dict[str, Any]) -> Dict[str, Any]:
    """
    Placeholder for a call to the Gemini API.
    This function would take the raw text and ask the LLM to perform
    several tasks in one go: summarize, generate social media content,
    suggest an image prompt, and extract key entities.
    """
    print(f"Calling mock Gemini API for analysis of: {raw_intel['headline']}")
    headline = raw_intel['headline']
    summary = raw_intel['summary']

    return {
        "summary": f"AI-generated summary: {summary}",
        "instagram_caption": f"🚨 SON DAKİKA: {headline}\n\n{summary}\n\n#Haber #Gündem #Türkiye",
        "instagram_hashtags": ["haber", "sondakika", "türkiye", "gündem"],
        "image_generation_prompt": f"A dramatic, photorealistic image representing the news: '{headline}'",
        "score_analysis_prompt": f"Analyzed '{headline}'. Keywords found. Source authority: {raw_intel.get('authority_tier', 3)}/5.",
        "entities": ["Turkey", "Government", "Economy"], # Mock entities
        "sentiment_score": 0.7 # Mock sentiment score (from -1.0 to 1.0)
    }

def save_briefing_to_db(briefing_data: Dict[str, Any]) -> NewsBriefing:
    """
    Placeholder for a CRUD function to save the briefing to the database.
    In a real app, this would use an active DB session.
    """
    print(f"Saving briefing '{briefing_data['headline']}' to the database...")
    # This is a mock save. It returns a NewsBriefing instance but doesn't persist it.
    # The real implementation will be part of the API/DB setup.
    mock_saved_briefing = NewsBriefing(**briefing_data)
    mock_saved_briefing.id = int(datetime.now().timestamp()) # Assign a mock ID
    return mock_saved_briefing

def send_notification_to_dashboard(briefing: NewsBriefing):
    """
    Placeholder for sending a real-time notification to the frontend.
    This would likely be implemented with WebSockets.
    """
    print("\n" + "="*80)
    print(f"🚀 ALERT! High-value news detected. Pushing to Command Center dashboard.")
    print(f"  ID: {briefing.id}")
    print(f"  Headline: {briefing.headline}")
    print(f"  Score: {briefing.news_value_score} (Threshold: {settings.NEWS_VALUE_THRESHOLD})")
    print("="*80 + "\n")

def get_briefing_from_db(briefing_id: str) -> Optional[NewsBriefing]:
    """Placeholder for fetching a briefing from the database."""
    print(f"Fetching briefing {briefing_id} from database...")
    # Return a mock object for demonstration
    return NewsBriefing(
        id=briefing_id,
        source_name="Mock Source",
        headline="Mock Headline for Posting",
        summary="This is the summary of the news that was approved.",
        source_url="http://example.com/mock-news",
        news_value_score=9,
        score_analysis_prompt="Mock analysis.",
        instagram_caption="This is the Instagram caption.",
        instagram_hashtags=["#mock", "#news"],
        image_generation_prompt="A mock image prompt.",
        status="approved"
    )

def generate_image_from_prompt(prompt: str) -> str:
    """Placeholder for DALL-E 3 or other image generation API call."""
    print(f"Generating image with prompt: '{prompt}'")
    # In a real implementation, this would return the URL or path to the downloaded image
    return "/tmp/generated_image.jpg"

def post_image_to_instagram(image_path: str, caption: str):
    """Placeholder for instagrapi posting logic."""
    print(f"Uploading {image_path} to Instagram with caption:\n---\n{caption}\n---")
    print("Post successful!")


# --- Celery App Initialization ---

app = celery.Celery(
    "sentinel_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['workers.tasks']
)
app.conf.update(
    task_track_started=True,
)


# --- Core Analyst & Sentinel Functions ---

def calculate_news_value(intel_item: Dict[str, Any], x_trends: List[str]) -> int:
    """
    Implements the multi-factor "News Value Algorithm" as described in the blueprint.

    The final score is a weighted sum of four factors, each scored from 0 to 10.
    """
    # 1. Keyword Analysis (Weight: 40%)
    text_to_scan = (intel_item['headline'] + " " + intel_item['summary']).lower()
    found_keywords = [kw for kw in settings.HIGH_IMPACT_KEYWORDS if kw in text_to_scan]
    keyword_score = min(10, len(found_keywords) * 2.5) # 4 keywords = max score

    # 2. Source Authority (Weight: 20%)
    authority_tier = intel_item.get('authority_tier', 3)
    authority_score = min(10, authority_tier * 2)

    # 3. Social Velocity (Weight: 30%)
    # Check if any words from the headline are in X trends
    item_words = set(re.findall(r'\w+', text_to_scan))
    is_trending = any(trend in item_words for trend in x_trends)
    social_velocity_score = 10 if is_trending else 2

    # 4. Sentiment Intensity (Weight: 10%)
    # This would come from the Gemini analysis in a real scenario.
    sentiment = intel_item.get('sentiment_score', 0.0)
    sentiment_intensity_score = min(10, abs(sentiment) * 10)

    # Calculate the weighted total score
    total_score = (
        (keyword_score * settings.KEYWORD_WEIGHT) +
        (authority_score * settings.SOURCE_AUTHORITY_WEIGHT) +
        (social_velocity_score * settings.SOCIAL_VELOCITY_WEIGHT) +
        (sentiment_intensity_score * settings.SENTIMENT_INTENSITY_WEIGHT)
    )

    # Uniqueness bonus (future implementation)
    # Could check DB for recent posts with same entities and add a bonus point.

    return round(total_score)


@app.task(name="tasks.analyze_and_alert_task")
def analyze_and_alert_task(raw_intel: Dict[str, Any]):
    """
    Celery task that orchestrates the full analysis of a raw intel item.
    """
    print(f"\n--- Analyzing: {raw_intel['headline']} ---")

    # 1. Get current X Trends
    x_trends = get_x_trends_for_turkey()

    # 2. Call Gemini for the full analysis package
    analysis_package = call_gemini_for_analysis(raw_intel)

    # Add sentiment score from analysis to the raw intel for scoring
    raw_intel['sentiment_score'] = analysis_package.get('sentiment_score', 0.0)

    # 3. Calculate the News Value Score
    score = calculate_news_value(raw_intel, x_trends)
    print(f"Calculated News Value Score: {score}")

    # 4. Assemble the complete briefing data for database insertion
    briefing_data = {
        "source_name": raw_intel['source_name'],
        "headline": raw_intel['headline'],
        "summary": analysis_package['summary'],
        "source_url": raw_intel['source_url'],
        "news_value_score": score,
        "score_analysis_prompt": analysis_package['score_analysis_prompt'],
        "instagram_caption": analysis_package['instagram_caption'],
        "instagram_hashtags": analysis_package['instagram_hashtags'],
        "image_generation_prompt": analysis_package['image_generation_prompt'],
        "entities": analysis_package['entities'],
        "status": "pending_review",
    }

    # 5. Save the complete briefing to the database
    saved_briefing = save_briefing_to_db(briefing_data)

    # 6. Check if score exceeds threshold and alert the dashboard
    if score >= settings.NEWS_VALUE_THRESHOLD:
        send_notification_to_dashboard(saved_briefing)
    else:
        print(f"Score {score} is below threshold ({settings.NEWS_VALUE_THRESHOLD}). Not sending alert.")
    print("--- Analysis Complete ---")


@app.task(name="tasks.post_to_instagram_task")
def post_to_instagram_task(briefing_id: str):
    """
    Triggered by user approval to generate an image and post to Instagram.
    """
    print("\n--- Instagram Post Task Initiated ---")
    # 1. Fetch the briefing data from the database
    briefing = get_briefing_from_db(briefing_id)
    if not briefing:
        print(f"Error: Briefing with ID {briefing_id} not found.")
        return

    # 2. Generate the image using the prompt from the briefing
    image_path = generate_image_from_prompt(briefing.image_generation_prompt)

    # 3. Construct the full caption with hashtags
    full_caption = briefing.instagram_caption + "\n\n" + " ".join(briefing.instagram_hashtags)

    # 4. Upload the image and caption to Instagram
    post_image_to_instagram(image_path, full_caption)

    # 5. Update the briefing status in the DB (placeholder)
    print(f"Updating status of briefing {briefing_id} to 'posted'.")
    print("--- Instagram Post Task Complete ---")


# --- Data Collector & Master Sweep Functions ---

def scrape_rss_feeds() -> List[Dict[str, Any]]:
    """Placeholder for the RSS feed scraping logic."""
    print("Scraping mock RSS feeds...")
    # This would iterate through sources from DB where type='rss'
    return [
        {
            "source_name": "Official News Agency",
            "headline": "Major Government Announcement on New Tax Policy",
            "summary": "The government has just announced a new set of tax reforms aimed at boosting the economy.",
            "source_url": "http://example.com/article1",
            "authority_tier": 5
        },
        {
            "source_name": "Niche Tech Blog",
            "headline": "New AI Chip Unveiled by Tech Giant",
            "summary": "A new chip promises to double the speed of AI computations.",
            "source_url": "http://techblog.example.com/ai-chip",
            "authority_tier": 2
        }
    ]

def scrape_telegram_channels() -> List[Dict[str, Any]]:
    """Placeholder for the Telegram scraping logic."""
    print("Scraping mock Telegram channels...")
    return [] # No mock data for now

def scrape_x_accounts() -> List[Dict[str, Any]]:
    """Placeholder for the X scraping logic."""
    print("Scraping mock X accounts...")
    return [] # No mock data for now


@app.task(name="tasks.trigger_master_sweep")
def trigger_master_sweep():
    """
    The main scheduled task that kicks off the entire data collection
    and analysis pipeline.
    """
    print("\n" + "*"*80)
    print(f"MASTER SWEEP INITIATED at {datetime.utcnow().isoformat()}")
    print("*"*80)

    # In a real implementation, we'd fetch active sources from the DB
    # For now, we call the placeholder scrapers directly.

    all_raw_intel = []
    all_raw_intel.extend(scrape_rss_feeds())
    all_raw_intel.extend(scrape_telegram_channels())
    all_raw_intel.extend(scrape_x_accounts())

    print(f"Found {len(all_raw_intel)} new items to analyze.")

    # In a real app, we'd also check against the DB to see if we've already
    # processed the source_url to avoid duplicates.

    for intel_item in all_raw_intel:
        # For each new item, trigger the analysis task asynchronously
        analyze_and_alert_task.delay(intel_item)

# --- Celery Beat Schedule ---

app.conf.beat_schedule = {
    'run-master-sweep-every-x-minutes': {
        'task': 'tasks.trigger_master_sweep',
        'schedule': settings.CHECK_INTERVAL_MINUTES * 60.0,  # schedule in seconds
    },
}