import requests

# User Story: As a user, I want to see the most frequently reported
# reactions in animal adverse event reports so that I can understand
# common safety issues.

BASE_URL = "https://api.fda.gov/animalandveterinary/event.json"


def get_top_reactions(limit: int = 10):
    """
    Fetch the most frequently reported reactions using openFDA count API.

    Args:
        limit: number of terms to return (top N)
        skip: number of terms to skip (pagination)

    Returns:
        A list of dicts like: [{"term": "...", "count": 123}, ...]
    """
    params = {
        "count": "reaction.veddra_term_name.exact",
        "limit": limit,
    }
    resp = requests.get(BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("results", [])


def print_results(title: str, results):
    print(title)
    for i, item in enumerate(results, start=1):
        print(f"{i:02d}. {item['term']} — {item['count']}")
    print()


if __name__ == "__main__":
    top20 = get_top_reactions(limit=20)

    page1 = top20[:10]
    # Show pagination
    page2 = top20[10:20]

    print_results("Top 1–10 reactions:", page1)
    print_results("Top 11–20 reactions:", page2)