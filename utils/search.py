import requests

def search_piped(query, limit=10):
    r = requests.get("https://piped.video/api/v1/search", params={"q": query, "region": "US"})
    r.raise_for_status()
    data = r.json()
    results = []
    for item in data:
        if item.get("type") == "video":
            results.append({
                "title": item["title"],
                "link": f"https://www.youtube.com/watch?v={item['id']}"
            })
            if len(results) >= limit:
                break
    return results
