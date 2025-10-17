import requests
import pandas as pd

# 🔑 Replace this with your Rainforest API key
API_KEY = "40C25ED0DBBB4859B69E101D4995CF6C"

def get_amazon_top_products(keyword, max_results=10):
    params = {
        'api_key': API_KEY,
        'type': 'search',
        'amazon_domain': 'amazon.in',
        'search_term': keyword,
        'page': 1
    }

    response = requests.get('https://api.rainforestapi.com/request', params=params)
    data = response.json()

    if 'search_results' not in data:
        print("⚠️ No search results found. Check your API key or query.")
        return []

    results = []
    for product in data['search_results'][:max_results]:
        title = product.get('title', 'N/A')
        price = product.get('price', {}).get('value', 'N/A')
        currency = product.get('price', {}).get('currency', '')
        rating = product.get('rating', 'N/A')
        reviews = product.get('reviews_total', 'N/A')
        link = product.get('link', '')

        results.append({
            "Product Title": title,
            "Price": f"{currency} {price}",
            "Rating": rating,
            "Reviews": reviews,
            "Link": link
        })

    return results

# 🛍 Example use
if __name__ == "__main__":
    keyword = input("Enter product keyword (e.g., 'wireless earbuds'): ")
    products = get_amazon_top_products(keyword, max_results=10)

    if products:
        df = pd.DataFrame(products)
        print(df)
        df.to_csv("winning_products.csv", index=False)
        print("\n✅ Saved to winning_products.csv")
