# app.py
import streamlit as st
import requests
import pandas as pd
import math
import matplotlib.pyplot as plt

# -------------------------------
# Page Setup
# -------------------------------
st.set_page_config(
    page_title="🔥 ZYVRO AI - Amazon Winning Product Finder",
    layout="wide"
)

# -------------------------------
# Branding Header
# -------------------------------
st.markdown("""
    <div style="text-align:center; font-size:32px; font-weight:bold; background:linear-gradient(90deg, #FF4B4B, #E63946, #F1C40F); 
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
    🔥 ZYVRO AI - Amazon Winning Product Finder
    </div>
""", unsafe_allow_html=True)
st.markdown("Find Amazon’s hidden goldmine products using AI-powered scoring 🚀")
st.markdown("---")

# -------------------------------
# Sidebar Settings
# -------------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    keyword = st.text_input("Search keyword", value="wireless earbuds")
    num_products = st.slider("Number of products to fetch", 5, 30, 12)
    compute_score = st.checkbox("Compute Winning Score (rating * log(reviews) / price)", value=True)
    run_button = st.button("Search Live")

# -------------------------------
# Rainforest API Key from Secrets
# -------------------------------
if "RAINFOREST_API_KEY" not in st.secrets:
    st.error("❌ Please add your RAINFOREST_API_KEY in Streamlit Secrets.")
    st.stop()
API_KEY = st.secrets["RAINFOREST_API_KEY"]

# -------------------------------
# Fetch Live Amazon Data
# -------------------------------
def fetch_rainforest_search(api_key, term, domain="amazon.in"):
    params = {
        "api_key": api_key,
        "type": "search",
        "amazon_domain": domain,
        "search_term": term
    }
    r = requests.get("https://api.rainforestapi.com/request", params=params, timeout=30)
    r.raise_for_status()
    return r.json()

# -------------------------------
# Normalize Product Data
# -------------------------------
def normalize_product(p):
    try:
        price_data = p.get("price")
        price = None
        if isinstance(price_data, dict):
            val = price_data.get("value")
            price = float(val) if val else None

        rating = float(p.get("rating") or 0)
        reviews = int(p.get("reviews") or 0)
        return {
            "title": p.get("title"),
            "price": price,
            "rating": rating,
            "reviews": reviews,
            "link": p.get("link"),
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
# Run App
# -------------------------------
if run_button:
    with st.spinner("Fetching live Amazon data..."):
        try:
            raw = fetch_rainforest_search(API_KEY, keyword)
        except Exception as e:
            st.error(f"API request failed: {e}")
            st.stop()

    results = raw.get("search_results") or []
    df = pd.DataFrame([normalize_product(p) for p in results if normalize_product(p)])

    if df.empty:
        st.warning("No products found for this keyword.")
        st.stop()

    if compute_score:
        df["Winning Score"] = df.apply(compute_winning_score, axis=1)
        df = df.sort_values("Winning Score", ascending=False)
    else:
        df = df.sort_values("reviews", ascending=False)

    # -------------------------------
    # Top 8 Products Graph
    # -------------------------------
    st.subheader("📈 Top 8 Winning Products Visualization")
    top8 = df.head(8).reset_index(drop=True)

    # Normalize factors for color intensity
    max_price = top8["price"].max() or 1
    max_reviews = top8["reviews"].max() or 1
    max_rating = top8["rating"].max() or 1

    # Color weight = higher score, higher rating, more reviews, lower price
    color_intensity = (
        (top8["Winning Score"] / top8["Winning Score"].max()) * 0.5
        + (top8["rating"] / max_rating) * 0.3
        + (top8["reviews"] / max_reviews) * 0.2
    )

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(
        top8["title"].str[:45],
        top8["Winning Score"],
        color=plt.cm.plasma(color_intensity)
    )

    for bar, score, price in zip(bars, top8["Winning Score"], top8["price"]):
        width = bar.get_width()
        ax.text(
            width + (max(top8["Winning Score"]) * 0.02),
            bar.get_y() + bar.get_height() / 2,
            f"{score:.2f} (₹{price:.0f})",
            va="center",
            fontsize=10,
            color="black",
            fontweight="bold"
        )

    ax.invert_yaxis()
    ax.set_xlabel("Winning Score", fontsize=12)
    ax.set_ylabel("Product", fontsize=12)
    ax.set_title(
        f"Realistic Product Insights for '{keyword}'",
        fontsize=14,
        fontweight="bold",
        color="#4F46E5"
    )
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    st.pyplot(fig)

    # -------------------------------
    # Products Table
    # -------------------------------
    st.subheader("🔍 Products Table")
    display_df = df[["title", "price", "rating", "reviews", "Winning Score", "link"]].copy()
    st.dataframe(display_df, height=300)

    # -------------------------------
    # Top 8 Product Details
    # -------------------------------
    st.subheader("🏆 Top 8 Product Details")
    for idx, row in top8.iterrows():
        st.markdown(f"### {row['title'][:70]}")
        st.markdown(f"- 💰 Price: ₹{row['price']}")
        st.markdown(f"- ⭐ Rating: {row['rating']} | 🗣️ Reviews: {row['reviews']}")
        st.markdown(f"- 🏁 Winning Score: {round(row['Winning Score'],4)}")
        st.markdown(f"- 🔗 [View on Amazon]({row['link']})")
        st.markdown("---")
