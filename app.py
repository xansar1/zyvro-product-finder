import streamlit as st
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------
# Streamlit Page Setup
# -------------------------------
st.set_page_config(page_title="Zyvro Product Finder", page_icon="🛍️", layout="wide")
st.title("🛍️ ZYVRO Product Finder")
st.markdown("### Find the best Amazon products using live data & smart ranking!")

# -------------------------------
# API Key Setup
# -------------------------------
api_key = st.secrets.get("RAINFOREST_API_KEY")
if not api_key:
    st.error("❌ Please add your `RAINFOREST_API_KEY` in Streamlit Secrets.")
    st.stop()

# -------------------------------
# Search Input
# -------------------------------
keyword = st.text_input("🔍 Enter a product keyword (example: wireless earbuds, laptop, smart watch)", "")

if st.button("Search Product Data"):
    if not keyword.strip():
        st.warning("⚠️ Please enter a product name to search.")
        st.stop()

    with st.spinner("Fetching live data from Amazon... 🔄"):
        url = "https://api.rainforestapi.com/request"
        params = {
            "api_key": api_key,
            "type": "search",
            "amazon_domain": "amazon.in",
            "search_term": keyword
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            st.error("❌ API request failed. Check your API key or network.")
            st.stop()

        data = response.json()
        # st.json(data)  # Uncomment this line if you want to debug JSON response

        products = data.get("search_results", [])
        if not products:
            st.warning("No products found. Try a different keyword.")
            st.stop()

        # -------------------------------
        # Convert JSON to DataFrame
        # -------------------------------
        df = pd.DataFrame([
            {
                "title": p.get("title"),
                "price": p.get("price", {}).get("value"),
                "rating": p.get("rating"),
                "reviews": p.get("reviews_total"),
                "image": p.get("image"),
                "link": p.get("link")
            }
            for p in products
        ])

        # Clean Data
        df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0)
        df["reviews"] = pd.to_numeric(df["reviews"], errors="coerce").fillna(0)

        # Compute "Winning Score"
        df["Winning Score"] = (df["rating"] * np.log1p(df["reviews"])) / (df["price"] + 1)
        df["Winning Score"] = df["Winning Score"].fillna(0)

        # -------------------------------
        # Top 8 Products Graph
        # -------------------------------
        st.subheader("📈 Top 8 Winning Products Visualization")

        top8 = df.sort_values("Winning Score", ascending=False).head(8)

        if top8["Winning Score"].sum() == 0:
            st.warning("⚠️ No valid numeric data to plot. Try another keyword.")
        else:
            max_score = top8["Winning Score"].max()
            color_intensity = (top8["Winning Score"] / max_score)

            fig, ax = plt.subplots(figsize=(10, 5))
            bars = ax.barh(top8["title"].str[:45], top8["Winning Score"],
                           color=plt.cm.plasma(color_intensity))
            for bar, score, price in zip(bars, top8["Winning Score"], top8["price"]):
                ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
                        f"{score:.2f} (₹{price:.0f})", va="center", fontsize=10)
            ax.invert_yaxis()
            ax.set_xlabel("Winning Score")
            st.pyplot(fig)

        # -------------------------------
        # Product Details with Images
        # -------------------------------
        st.subheader("🏆 Top 8 Product Details")

        for idx, row in top8.iterrows():
            st.markdown(f"### {row['title']}")
            if pd.notna(row.get("image")) and str(row["image"]).startswith("http"):
                st.image(row["image"], width=200)
            else:
                st.write("🖼️ *No image available*")

            st.write(f"💰 **Price:** ₹{row['price']}")
            st.write(f"⭐ **Rating:** {row['rating']} | 💬 Reviews: {row['reviews']}")
            st.write(f"🏁 **Winning Score:** {round(row['Winning Score'], 4)}")
            st.markdown(f"[🔗 View on Amazon]({row['link']})")
            st.markdown("---")

        # -------------------------------
        # Data Table
        # -------------------------------
        st.subheader("📊 Full Product Data Table")
        st.dataframe(df)

        st.success("✅ Data fetched successfully from live API!")
