import requests
import json

def test_recommendation(user_id=276725, top_k=5):
    """Test the book recommendation endpoint."""
    url = "http://localhost:8000/recommend"
    payload = {
        "user_id": user_id,
        "top_k": top_k
    }

    print(f"Requesting book recommendations for User {user_id}...")
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Response Successful!")
            data = response.json()
            print(f"\nTop {top_k} book recommendations for User {user_id}:")
            for i, rec in enumerate(data['recommendations'], 1):
                print(f"  {i}. [{rec['isbn']}] {rec['book_title']} by {rec['book_author']} (score: {rec['score']:.4f})")
        else:
            print(f"Error {response.status_code}: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure the FastAPI server is running at http://localhost:8000")


def test_stats():
    """Test the stats endpoint."""
    url = "http://localhost:8000/stats"
    print("\nFetching system stats...")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Error {response.status_code}: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API.")


def test_invalid_user():
    """Test error handling for unknown user."""
    url = "http://localhost:8000/recommend"
    print("\nTesting with unknown user ID 999999...")
    try:
        response = requests.post(url, json={"user_id": 999999, "top_k": 5})
        print(f"Status: {response.status_code} | Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API.")


if __name__ == "__main__":
    test_recommendation(user_id=276725)
    test_stats()
    test_invalid_user()
