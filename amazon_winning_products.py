import requests
import pandas as pd
import os
from dotenv import load_dotenv

# ---------------- LOAD ENV ----------------
load_dotenv()
API_KEY = os.getenv("RAINFOREST_API_KEY")


def competition_level(reviews):
    if reviews < 200:
        return "Low"
    elif reviews < 1000:
        return "Medium"
    return "High"


def get_amazon_top_products(keyword, marketplace="amazon.in", max_results=10):
    params = {
        "api_key": API_KEY,
        "type": "search",
        "amazon_domain": marketplace,
        "search_term": keyword,
        "page": 1
    }

    response = requests.get(
        "https://api.rainforestapi.com/request",
        params=params
    )

    data = response.json()

    if "search_results" not in data:
        print("⚠️ No search results found. Check API key or keyword.")
        return pd.DataFrame()

    rows = []

    for product in data["search_results"][:max_results]:
        title = product.get("title", "N/A")
        price = product.get("price", {}).get("value", 0)
        currency = product.get("price", {}).get("currency", "INR")
        rating = product.get("rating", 0)
        reviews = product.get("reviews_total", 0)
        link = product.get("link", "")

        rows.append({
            "Product Title": title,
            "Price": price,
            "Currency": currency,
            "Rating": rating,
            "Reviews": reviews,
            "Competition": competition_level(reviews),
            "Link": link
        })

    df = pd.DataFrame(rows)

    # ---------------- SMART SCORE ----------------
    max_price = max(df["Price"].max(), 1)

    df["Winning Score"] = (
        (df["Rating"] * 0.25) +
        (df["Reviews"].apply(lambda x: min(x / 5000, 1)) * 0.25) +
        ((1 - (df["Price"] / max_price)) * 0.20) +
        (df["Product Title"].str.len().apply(lambda x: 1 if x < 80 else 0.5) * 0.15) +
        (df["Reviews"].apply(lambda x: 1 if x < 500 else 0.4) * 0.15)
    ) * 100

    # ---------------- BUSINESS METRICS ----------------
    df["Estimated Margin"] = (df["Price"] * 0.35).round(2)
    df["Suggested Sourcing Cost"] = (df["Price"] * 0.45).round(2)

    return df.sort_values("Winning Score", ascending=False)


# ---------------- CLI MODE ----------------
if __name__ == "__main__":
    keyword = input("Enter product keyword: ")

    df = get_amazon_top_products(
        keyword=keyword,
        marketplace="amazon.in",
        max_results=10
    )

    if not df.empty:
        print(df[[
            "Product Title",
            "Price",
            "Rating",
            "Reviews",
            "Competition",
            "Winning Score"
        ]])

        df.to_csv("winning_products.csv", index=False)
        print("\n✅ Saved to winning_products.csv")
