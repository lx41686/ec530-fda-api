import requests

# User Story: As a user, I want to see the most frequently reported
# reactions in animal adverse event reports so that I can understand
# common safety issues.

URL = "https://api.fda.gov/animalandveterinary/event.json"

params = {
    "count": "reaction.veddra_term_name.exact",
    "limit": 10,
}

resp = requests.get(URL, params=params, timeout=30)
print("Status:", resp.status_code)
resp.raise_for_status()  # If not 200, raise error and reasons

data = resp.json()

# Print top 10
for i, item in enumerate(data["results"], start=1):
    print(f"{i:02d}. {item['term']} — {item['count']}")