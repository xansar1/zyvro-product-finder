import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
from io import BytesIO
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()
API_KEY = os.getenv("RAINFOREST_API_KEY")

# App title
st.set_page_config(page_title="Zyvro AI - Amazon Winning Product Finder", layout="wide")
st.title("🔥 ZYVRO AI - Amazon Winning Product Finder")
st.write("Find Amazon's hidden goldmine products using AI-powered scoring 🚀")

# Search bar
keyword = st.text_input("🔍 Enter a product keyword", "wireless earbuds")

# If user searches
if keyword:
    st.subheader("📦 Fetching Live Amazon Data...")

    # Fetch from Rainforest API
    url = "https://api.rainforestapi.com/request"
    params = {
        "api_key": API_KEY,
        "type": "search",
        "amazon_domain": "amazon.in",
        "search_term": keyword,
        "page": "1"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "search_results" in data:
        products = data["search_results"]

        # Build dataframe
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

        # 🔧 Data Cleaning
        df["price"] = (
            df["price"]
            .astype(str)
            .str.replace("₹", "", regex=False)
            .str.replace(",", "", regex=False)
        )
        df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0)
        df["reviews"] = pd.to_numeric(df["reviews"], errors="coerce").fillna(0)

        # 💡 Compute Winning Score
        df["Winning Score"] = (
            (df["rating"] * 0.6) + (df["reviews"].apply(lambda x: min(x / 1000, 1)) * 0.4)
        )

        # Sort top 8
        top8 = df.sort_values("Winning Score", ascending=False).head(8).reset_index(drop=True)

        # 🎯 Display Visualization
        st.subheader("📈 Top 8 Winning Products Visualization")

        valid_df = top8[(top8["price"] > 0) & (top8["rating"] > 0)]
        if not valid_df.empty:
            plt.figure(figsize=(10, 5))
            plt.barh(valid_df["title"], valid_df["Winning Score"], color="skyblue")
            plt.xlabel("Winning Score")
            plt.ylabel("Product")
            plt.title(f"Realistic Product Insights for '{keyword}'", fontweight="bold", color="purple")
            plt.tight_layout()

            buf = BytesIO()
            plt.savefig(buf, format="png")
            st.image(buf)
        else:
            st.warning("⚠️ No valid numeric data to plot. Try another keyword.")

        # 📊 Show Product Table
        st.subheader("🔎 Products Table")
        st.dataframe(top8[["title", "price", "rating", "reviews", "Winning Score", "link"]])

        # 🏆 Show Individual Product Details
        st.subheader("🏆 Top 8 Product Details")
        for idx, row in top8.iterrows():
            st.markdown(f"### {row['title']}")
            if row["image"]:
                st.image(row["image"], width=250)
            else:
                st.info("Image not available")
            st.markdown(f"""
            - 💰 **Price:** ₹{row['price']}
            - ⭐ **Rating:** {row['rating']} | 💬 **Reviews:** {row['reviews']}
            - 🏁 **Winning Score:** {round(row['Winning Score'], 2)}
            - 🔗 [**View on Amazon**]({row['link']})
            """)

    else:
        st.error("❌ Could not fetch product data. Check your API key or keyword.")
