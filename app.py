import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="ZYVRO AI - Amazon Winning Product Finder",
    layout="wide"
)

st.title("🔥 ZYVRO AI - Amazon Winning Product Finder")
st.write(
    "Upload Amazon product research CSV and discover "
    "high-potential winning products using AI-powered seller intelligence 🚀"
)

# ---------------- CSV FORMAT GUIDE ----------------
st.info("""
📁 Required CSV columns:
title, price, rating, reviews, category
""")

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader(
    "📂 Upload Product Research CSV",
    type=["csv"]
)

# ---------------- FUNCTIONS ----------------
def competition_level(reviews):
    if reviews < 200:
        return "Low"
    elif reviews < 1000:
        return "Medium"
    return "High"

# ---------------- MAIN APP ----------------
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # ---------------- CLEAN DATA ----------------
    required_cols = ["title", "price", "rating", "reviews", "category"]

    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        st.error(f"❌ Missing columns: {', '.join(missing_cols)}")
        st.stop()

    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0)
    df["reviews"] = pd.to_numeric(df["reviews"], errors="coerce").fillna(0)

    max_price = max(df["price"].max(), 1)

    # ---------------- SMART WINNING SCORE ----------------
    df["Winning Score"] = (
        (df["rating"] * 0.30) +
        (df["reviews"].apply(lambda x: min(x / 5000, 1)) * 0.25) +
        ((1 - (df["price"] / max_price)) * 0.20) +
        (df["title"].str.len().apply(lambda x: 1 if x < 80 else 0.5) * 0.10) +
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
        f"Category: {best['category']} | "
        f"Competition: {best['Competition']} | "
        f"Winning Score: {round(best['Winning Score'], 2)}"
    )

    # ---------------- VISUALIZATION ----------------
    st.subheader("📈 Top 8 Winning Products")

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.barh(top8["title"], top8["Winning Score"])
    ax.set_xlabel("Winning Score")
    ax.set_ylabel("Product")
    ax.set_title("Top Winning Product Opportunities")
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format="png")
    st.image(buf)

    # ---------------- TABLE ----------------
    st.subheader("📊 Winning Product Intelligence Table")
    st.dataframe(
        top8[[
            "title",
            "category",
            "price",
            "rating",
            "reviews",
            "Competition",
            "Estimated Margin",
            "Suggested Sourcing Cost",
            "Winning Score"
        ]]
    )

    # ---------------- PRODUCT BREAKDOWN ----------------
    st.subheader("🏆 Top 8 Product Breakdown")

    for _, row in top8.iterrows():
        st.markdown(f"### {row['title']}")
        st.markdown(f"""
- 📦 **Category:** {row['category']}
- 💰 **Price:** ₹{row['price']}
- ⭐ **Rating:** {row['rating']}
- 💬 **Reviews:** {row['reviews']}
- ⚔️ **Competition:** {row['Competition']}
- 📈 **Winning Score:** {round(row['Winning Score'], 2)}
- 💵 **Estimated Margin:** ₹{row['Estimated Margin']}
- 🏭 **Suggested Sourcing Cost:** ₹{row['Suggested Sourcing Cost']}
""")
        st.divider()

    # ---------------- CSV EXPORT ----------------
    csv = top8.to_csv(index=False).encode("utf-8")

    st.download_button(
        "📥 Download Winning Products CSV",
        data=csv,
        file_name="winning_products_output.csv",
        mime="text/csv"
    )

else:
    st.info("📂 Upload a CSV file to start product intelligence.")
