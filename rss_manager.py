import feedparser

def fetch_rss_feeds(feed_urls, limit=10):
    articles = []

    for url in feed_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            image_url = None
            if "media_content" in entry:
                image_url = entry.media_content[0].get("url", None)
            elif "links" in entry:
                for link in entry.links:
                    if link.get("type", "").startswith("image"):
                        image_url = link.get("href")
                        break
            elif "image" in entry:
                image_url = entry.image.get("href", None)
            elif "summary_detail" in entry and "src=" in entry.summary_detail.value:
                start = entry.summary_detail.value.find("src=")
                if start != -1:
                    start += 5
                    end = entry.summary_detail.value.find('"', start)
                    image_url = entry.summary_detail.value[start:end]

            articles.append({
                "title": entry.title,
                "link": entry.link,
                "published": entry.get("published", "Unknown"),
                "image": image_url
            })

    articles = sorted(articles, key=lambda x: x.get("published", ""), reverse=True)
    return articles[:limit]
