"""
News sources focused on Thailand tourism.
Only English language sources that regularly publish tourism related content.
"""

NEWS_SOURCES = [
    {
        "name": "TAT Newsroom",
        "base_url": "https://www.tatnews.org",
        "rss_url": "https://www.tatnews.org/feed/",
        "category_urls": [
            "https://www.tatnews.org/category/thailand-tourism-updates/",
            "https://www.tatnews.org/category/thailand-tourism-news/",
            "https://www.tatnews.org/category/thailand-events-festivals/",
        ],
        "type": "rss_and_scrape"
    },
    {
        "name": "The Nation Thailand",
        "base_url": "https://www.nationthailand.com",
        "rss_url": "https://www.nationthailand.com/rss",
        "category_urls": [
            "https://www.nationthailand.com/news/tourism",
        ],
        "type": "rss_and_scrape"
    },
    {
        "name": "Bangkok Post",
        "base_url": "https://www.bangkokpost.com",
        "rss_url": "https://www.bangkokpost.com/rss/data/topstories.xml",
        "category_urls": [
            "https://www.bangkokpost.com/thailand/tourism",
            "https://www.bangkokpost.com/travel",
        ],
        "type": "rss_and_scrape"
    },
    {
        "name": "The Thaiger",
        "base_url": "https://thethaiger.com",
        "rss_url": "https://thethaiger.com/feed",
        "category_urls": [
            "https://thethaiger.com/news",
            "https://thethaiger.com/hot-news",
        ],
        "type": "rss"
    },
    {
        "name": "Khaosod English",
        "base_url": "https://www.khaosodenglish.com",
        "rss_url": "https://www.khaosodenglish.com/feed/",
        "category_urls": [],
        "type": "rss"
    },
    {
        "name": "Phuket News",
        "base_url": "https://www.thephuketnews.com",
        "rss_url": "https://www.thephuketnews.com/rss/",
        "category_urls": [],
        "type": "rss"
    },
    {
        "name": "Pattaya Mail",
        "base_url": "https://www.pattayamail.com",
        "rss_url": "https://www.pattayamail.com/feed",
        "category_urls": [],
        "type": "rss"
    },
]

TOURISM_KEYWORDS = [
    "tourism", "tourist", "tourists", "travel", "traveller", "traveler",
    "visa", "immigration", "arrival", "hotel", "hotels", "resort",
    "attraction", "attractions", "temple", "beach", "island", "phuket",
    "pattaya", "chiang mai", "bangkok", "songkran", "loy krathong",
    "festival", "tat", "tourism authority", "airport", "flight",
    "safety", "advisory", "scam", "flood", "weather", "destination",
    "accommodation", "booking", "visitor", "visitors", "arrival card",
    "tdac", "exemption", "overstay", "border", "national park"
]
