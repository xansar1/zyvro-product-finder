import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
from io import BytesIO
import os
from dotenv import load_dotenv

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="ZYVRO AI - Amazon Winning Product Finder",
    layout="wide"
)

load_dotenv()
API_KEY = os.getenv("RAINFOREST_API_KEY")

st.title("🔥 ZYVRO AI - Amazon Winning Product Finder")
st.write("Find Amazon hidden goldmine products using AI-powered seller intelligence 🚀")

# ---------------- USER INPUT ----------------
market = st.selectbox(
    "🌍 Select Amazon Marketplace",
    ["amazon.in", "amazon.com", "amazon.ae", "amazon.co.uk"]
)

keyword = st.text_input(
    "🔍 Enter product keyword",
    "wireless earbuds"
)

# ---------------- FUNCTIONS ----------------
def competition_level(reviews):
    if reviews < 200:
        return "Low"
    elif reviews < 1000:
        return "Medium"
    return "High"

# ---------------- MAIN SEARCH ----------------
if keyword:
    st.subheader(f"📦 Searching winning products in {market} ...")

    url = "https://api.rainforestapi.com/request"
    params = {
        "api_key": API_KEY,
        "type": "search",
        "amazon_domain": market,
        "search_term": keyword,
        "page": "1"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "search_results" in data:
        products = data["search_results"]

        df = pd.DataFrame([
            {
                "title": p.get("title", ""),
                "price": p.get("price", {}).get("value", None),
                "currency": p.get("price", {}).get("currency", "INR"),
                "rating": p.get("rating", 0),
                "reviews": p.get("reviews_total", 0),
                "link": p.get("link", ""),
                "image": p.get("image", "")
            }
            for p in products
        ])

        # ---------------- CLEAN DATA ----------------
        df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0)
        df["reviews"] = pd.to_numeric(df["reviews"], errors="coerce").fillna(0)

        max_price = max(df["price"].max(), 1)

        # ---------------- SMART WINNING SCORE ----------------
        df["Winning Score"] = (
            (df["rating"] * 0.25) +
            (df["reviews"].apply(lambda x: min(x / 5000, 1)) * 0.25) +
            ((1 - (df["price"] / max_price)) * 0.20) +
            (df["title"].str.len().apply(lambda x: 1 if x < 80 else 0.5) * 0.15) +
            (df["reviews"].apply(lambda x: 1 if x < 500 else 0.4) * 0.15)
        ) * 100

        # ---------------- BUSINESS INSIGHTS ----------------
        df["Competition"] = df["reviews"].apply(competition_level)
        df["Estimated Margin"] = (df["price"] * 0.35).round(2)
        df["Suggested Sourcing Cost"] = (df["price"] * 0.45).round(2)

        # ---------------- TOP PRODUCTS ----------------
        top8 = (
            df.sort_values("Winning Score", ascending=False)
            .head(8)
            .reset_index(drop=True)
        )

        # ---------------- BEST OPPORTUNITY ----------------
        best = top8.iloc[0]

        st.success(
            f"🚀 Best Opportunity: {best['title']} | "
            f"Competition: {best['Competition']} | "
            f"Winning Score: {round(best['Winning Score'], 2)}"
        )

        # ---------------- VISUALIZATION ----------------
        st.subheader("📈 Top 8 Winning Products")

        valid_df = top8[top8["Winning Score"] > 0]

        if not valid_df.empty:
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.barh(valid_df["title"], valid_df["Winning Score"])
            ax.set_xlabel("Winning Score")
            ax.set_ylabel("Product")
            ax.set_title(f"Best Products for '{keyword}'")
            plt.tight_layout()

            buf = BytesIO()
            plt.savefig(buf, format="png")
            st.image(buf)
        else:
            st.warning("⚠️ No valid products found.")

        # ---------------- TABLE ----------------
        st.subheader("📊 Winning Product Intelligence Table")
        st.dataframe(
            top8[[
                "title",
                "price",
                "rating",
                "reviews",
                "Competition",
                "Estimated Margin",
                "Suggested Sourcing Cost",
                "Winning Score",
                "link"
            ]]
        )

        # ---------------- PRODUCT CARDS ----------------
        st.subheader("🏆 Top 8 Product Breakdown")

        for _, row in top8.iterrows():
            st.markdown(f"### {row['title']}")

            if row["image"]:
                st.image(row["image"], width=250)

            st.markdown(f"""
- 💰 **Price:** {row['currency']} {row['price']}
- ⭐ **Rating:** {row['rating']}
- 💬 **Reviews:** {row['reviews']}
- ⚔️ **Competition:** {row['Competition']}
- 📈 **Winning Score:** {round(row['Winning Score'], 2)}
- 💵 **Estimated Margin:** {row['Estimated Margin']}
- 🏭 **Suggested Sourcing Cost:** {row['Suggested Sourcing Cost']}
- 🔗 [View on Amazon]({row['link']})
""")

            st.divider()

        # ---------------- CSV EXPORT ----------------
        csv = top8.to_csv(index=False).encode("utf-8")

        st.download_button(
            "📥 Download Winning Products CSV",
            data=csv,
            file_name=f"{keyword}_winning_products.csv",
            mime="text/csv"
        )

    else:
        st.error("❌ Could not fetch product data. Check API key, credits, or keyword.")
