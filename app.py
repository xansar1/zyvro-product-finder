# app.py
import os
import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import math

# -------------------------------
# Streamlit page setup
# -------------------------------
st.set_page_config(page_title="🔥 ZYVRO AI - Winning Product Finder", layout="wide")
st.title("🔥 ZYVRO AI - Amazon Winning Product Finder")
st.markdown("Find Amazon’s hidden goldmine products using AI-powered ranking 🚀")

# -------------------------------
# Sidebar settings
# -------------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    keyword = st.text_input("Search keyword", value="wireless earbuds")
    num_products = st.slider("Number of products to fetch", 5, 30, 12)
    compute_score = st.checkbox("Compute Winning Score (rating * log(reviews) / price)", value=True)
    run_button = st.button("Run Live Search")

# -------------------------------
# Get API key from Streamlit Secrets
# -------------------------------
API_KEY = st.secrets.get("RAINFOREST_API_KEY")
if not API_KEY:
    st.error("❌ Please add your RAINFOREST_API_KEY in Streamlit Secrets.")
    st.stop()

# -------------------------------
# Fetch data from Rainforest API
# -------------------------------
def fetch_rainforest_search(api_key, term, domain="amazon.in"):
    params = {
        "api_key": api_key,
        "type": "search",
        "amazon_domain": domain,
        "search_term": term,
    }
    r = requests.get("https://api.rainforestapi.com/request", params=params, timeout=30)
    r.raise_for_status()
    return r.json()

# -------------------------------
# Normalize product data
# -------------------------------
def normalize_product(p):
    try:
        # Price
        price_data = p.get("price")
        price = None
        if isinstance(price_data, dict):
            val = price_data.get("value")
            if val and val > 100000:
                price = round(val / 100.0, 2)
            else:
                price = float(val) if val else None

        # Rating & Reviews
        rating = float(p.get("rating") or 0)
        reviews = int(p.get("reviews") or 0)

        # Thumbnail (first image if exists)
        thumbnail = None
        images = p.get("images")
        if images and isinstance(images, list) and len(images) > 0:
            thumbnail = images[0]

        return {
            "title": p.get("title"),
            "price": price,
            "rating": rating,
            "reviews": reviews,
            "link": p.get("link"),
            "thumbnail": thumbnail,
            "asin": p.get("asin")
        }
    except:
        return None

# -------------------------------
# Compute Winning Score
# -------------------------------
def compute_winning_score(row):
    r = row.get("rating") or 0
    rev = row.get("reviews") or 0
    p = row.get("price") or 0
    try:
        return (r * math.log1p(rev)) / (p + 1)
    except:
        return 0.0

# -------------------------------
# Run live search
# -------------------------------
if run_button:
    with st.spinner("Fetching live data from Rainforest API..."):
        try:
            raw = fetch_rainforest_search(API_KEY, keyword)
        except Exception as e:
            st.error(f"⚠️ API request failed: {e}")
            st.stop()

    results = raw.get("search_results") or []
    df = pd.DataFrame([normalize_product(p) for p in results if normalize_product(p)])

    if df.empty:
        st.warning("No products found for this keyword.")
        st.stop()

    # Compute Winning Score
    if compute_score:
        df["Winning Score"] = df.apply(compute_winning_score, axis=1)
        df = df.sort_values("Winning Score", ascending=False)
    else:
        df = df.sort_values("reviews", ascending=False)

    # -------------------------------
    # Top 8 Products Graph (Realistic Visual)
    # -------------------------------
    st.subheader("📈 Top 8 Winning Products Visualization")
    top8 = df.head(8).reset_index(drop=True)

    # Normalize factors for color intensity
    max_price = top8["price"].max() or 1
    max_reviews = top8["reviews"].max() or 1
    max_rating = top8["rating"].max() or 1

    color_intensity = (
        (top8["Winning Score"] / top8["Winning Score"].max()) * 0.5 +
        (top8["rating"] / max_rating) * 0.3 +
        (top8["reviews"] / max_reviews) * 0.2
    )

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(top8["title"].str[:45], top8["Winning Score"], color=plt.cm.plasma(color_intensity))

    for bar, score, price in zip(bars, top8["Winning Score"], top8["price"]):
        width = bar.get_width()
        ax.text(width + (max(top8["Winning Score"]) * 0.02),
                bar.get_y() + bar.get_height()/2,
                f"{score:.2f} (₹{price:.0f})",
                va="center", fontsize=10, color="black", fontweight="bold")

    ax.invert_yaxis()
    ax.set_xlabel("Winning Score", fontsize=12)
    ax.set_ylabel("Product", fontsize=12)
    ax.set_title(f"Realistic Product Insights for '{keyword}'", fontsize=14, fontweight="bold", color="#4F46E5")
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    st.pyplot(fig)

    # -------------------------------
    # Products Table
    # -------------------------------
    st.subheader("🔍 All Products Table")
    display_df = df[["title","price","rating","reviews","Winning Score","link"]].copy()
    st.dataframe(display_df, height=300)

    # -------------------------------
    # Top 8 Product Cards
    # -------------------------------
    st.subheader("🏆 Top 8 Product Details")
    for idx, row in top8.iterrows():
        st.markdown(f"### {row['title'][:70]}")
        if row["thumbnail"]:
            st.image(row["thumbnail"], width=200)
        else:
            st.image("https://via.placeholder.com/200?text=No+Image", width=200)
        st.markdown(f"- 💰 Price: ₹{row['price']}")
        st.markdown(f"- ⭐ Rating: {row['rating']} | 🗣️ Reviews: {row['reviews']}")
        st.markdown(f"- 🏁 Winning Score: {round(row['Winning Score'],4)}")
        st.markdown(f"- 🔗 [View on Amazon]({row['link']})")
        st.markdown("---")
