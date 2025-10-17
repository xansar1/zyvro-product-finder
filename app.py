import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import math
import requests

# -------------------------------
# Streamlit Page Setup
# -------------------------------
st.set_page_config(page_title="🔥 ZYVRO AI - Amazon Winning Product Finder", layout="wide")

# -------------------------------
# Custom Premium CSS
# -------------------------------
st.markdown("""
    <style>
        body { background-color: #0E1117; color: white; }
        [data-testid="stSidebar"] { background-color: #161A20; color: white; }
        .hero {
            text-align: center;
            background: linear-gradient(135deg, #1E1E2F, #2C2C3C);
            padding: 2rem 0;
            border-radius: 15px;
            box-shadow: 0 0 15px rgba(255,75,75,0.3);
            margin-bottom: 2rem;
        }
        .hero h1 {
            font-size: 45px;
            background: linear-gradient(90deg, #FF4B4B, #FFB300, #FF4B4B);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 900;
            letter-spacing: 1.2px;
        }
        .hero p {
            color: #C7C7C7;
            font-size: 18px;
            margin-top: -10px;
        }
        .stTextInput>div>div>input {
            text-align: center;
            border-radius: 10px;
            height: 45px;
            font-size: 18px;
        }
        .stButton>button {
            width: 100%;
            background: linear-gradient(90deg, #FF4B4B, #E63946);
            color: white;
            font-size: 18px;
            font-weight: bold;
            border-radius: 10px;
            border: none;
            transition: 0.3s ease-in-out;
        }
        .stButton>button:hover {
            transform: scale(1.05);
            background: linear-gradient(90deg, #E63946, #FF4B4B);
        }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# Hero Section
# -------------------------------
st.markdown("""
    <div class="hero">
        <h1>🔥 ZYVRO AI - Amazon Winning Product Finder</h1>
        <p>Find Amazon’s hidden goldmine products using AI-powered ranking 🚀</p>
    </div>
""", unsafe_allow_html=True)

# -------------------------------
# Sidebar Controls
# -------------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    num_products = st.slider("Number of Products", 5, 30, 12)
    compute_score = st.checkbox("Compute Winning Score", value=True)

# -------------------------------
# Centered Search Bar
# -------------------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    keyword = st.text_input("Enter a keyword to search Amazon:", value="wireless earbuds")
    run_button = st.button("🔍 Search Live Products")

# -------------------------------
# Rainforest API Function
# -------------------------------
def get_live_data(keyword, n=12):
    api_key = "40C25ED0DBBB4859B69E101D4995CF6C"
    url = "https://api.rainforestapi.com/request"
    params = {
        "api_key": api_key,
        "type": "search",
        "amazon_domain": "amazon.in",
        "search_term": keyword
    }

    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        st.error(f"⚠️ API request failed: {e}")
        return pd.DataFrame()

    products = []
    for item in data.get("search_results", [])[:n]:
        title = item.get("title")
        link = item.get("link")
        price_info = item.get("price", {})
        price = price_info.get("value", 0)
        rating = item.get("rating", 0)
        reviews = item.get("reviews", 0)
        thumbnail = item.get("image", "")
        if title and price:
            products.append({
                "title": title,
                "price": price,
                "rating": rating,
                "reviews": reviews,
                "link": link,
                "thumbnail": thumbnail
            })
    return pd.DataFrame(products)

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
# Main App Logic
# -------------------------------
if run_button:
    st.info("Fetching live Amazon data... please wait ⏳")

    df = get_live_data(keyword, num_products)
    if df.empty:
        st.warning("No products found. Try a different keyword.")
        st.stop()

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
    max_price = top8["price"].max() or 1
    max_reviews = top8["reviews"].max() or 1
    max_rating = top8["rating"].max() or 1

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
    # Product Table
    # -------------------------------
    st.subheader("🔍 Products Table")
    display_df = df[["title", "price", "rating", "reviews", "Winning Score", "link"]].copy()
    st.dataframe(display_df, height=350)

    # -------------------------------
    # Product Cards
    # -------------------------------
    st.subheader("🏆 Top 8 Product Details")
    for idx, row in top8.iterrows():
        st.markdown(f"### {row['title'][:70]}")
        if row["thumbnail"]:
            st.image(row["thumbnail"], width=220)
        st.markdown(f"- 💰 Price: ₹{row['price']}")
        st.markdown(f"- ⭐ Rating: {row['rating']} | 🗣️ Reviews: {row['reviews']}")
        st.markdown(f"- 🏁 Winning Score: {round(row['Winning Score'], 4)}")
        st.markdown(f"- 🔗 [View on Amazon]({row['link']})")
        st.markdown("---")
