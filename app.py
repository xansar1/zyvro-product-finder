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


def trend_label(score):
    if score > 70:
        return "🚀 Rising"
    elif score > 40:
        return "📈 Stable"
    return "📉 Declining"


# ---------------- MAIN APP ----------------
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    required_cols = ["title", "price", "rating", "reviews", "category"]
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        st.error(f"❌ Missing columns: {', '.join(missing_cols)}")
        st.stop()

    # ---------------- CLEAN DATA ----------------
    df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0)
    df["reviews"] = pd.to_numeric(df["reviews"], errors="coerce").fillna(0)

    max_price = max(df["price"].max(), 1)

    # ---------------- WINNING SCORE ----------------
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

    # ---------------- TREND MOMENTUM ----------------
    df["Trend Score"] = (
        (df["rating"] * 10) +
        (df["reviews"].apply(lambda x: min(x / 100, 50)))
    )
    df["Trend Status"] = df["Trend Score"].apply(trend_label)

    # ---------------- TOP PRODUCTS ----------------
    top8 = (
        df.sort_values("Winning Score", ascending=False)
        .head(8)
        .reset_index(drop=True)
    )

    best = top8.iloc[0]

    st.success(
        f"🚀 Best Opportunity: {best['title']} | "
        f"{best['Trend Status']} | "
        f"Winning Score: {round(best['Winning Score'], 2)}"
    )

    # ---------------- CHART ----------------
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
    st.subheader("📊 Product Intelligence Table")
    st.dataframe(
        top8[[
            "title",
            "category",
            "price",
            "rating",
            "reviews",
            "Competition",
            "Trend Status",
            "Estimated Margin",
            "Winning Score"
        ]]
    )

    # ---------------- ROI CALCULATOR ----------------
    st.subheader("💵 Profit & ROI Simulator")

    selected_product = st.selectbox(
        "Select Product for ROI Analysis",
        top8["title"]
    )

    selected_row = top8[top8["title"] == selected_product].iloc[0]

    selling_price = st.number_input(
        "Selling Price",
        value=float(selected_row["price"]),
        min_value=1.0
    )

    sourcing_cost = st.number_input(
        "Sourcing Cost",
        value=float(selected_row["Suggested Sourcing Cost"]),
        min_value=0.0
    )

    amazon_fee_percent = st.slider("Amazon Fee %", 1, 40, 15)
    ads_cost = st.number_input("Ads Cost per Sale", value=50.0)
    shipping_cost = st.number_input("Shipping Cost", value=40.0)

    amazon_fee = selling_price * (amazon_fee_percent / 100)

    net_profit = (
        selling_price
        - sourcing_cost
        - amazon_fee
        - ads_cost
        - shipping_cost
    )

    profit_margin = (net_profit / selling_price) * 100
    roi = (net_profit / sourcing_cost) * 100 if sourcing_cost > 0 else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Net Profit", f"₹{round(net_profit,2)}")
    c2.metric("📈 Margin %", f"{round(profit_margin,2)}%")
    c3.metric("🚀 ROI %", f"{round(roi,2)}%")

    if roi > 40 and profit_margin > 20:
        st.success("✅ Strong launch opportunity")
    elif roi > 20:
        st.warning("⚠️ Moderate opportunity")
    else:
        st.error("❌ Weak profitability")

    # ---------------- MARKET GAP FINDER ----------------
    st.subheader("🎯 Market Gap Finder")

    gap_df = top8[
        (top8["Competition"] != "High") &
        (top8["Trend Status"] != "📉 Declining") &
        (top8["Winning Score"] > 60)
   ].copy()

   if not gap_df.empty:
       best_gap = gap_df.iloc[0]

       st.success(
           f"🚀 Best Market Gap: {best_gap['title']} | "
           f"{best_gap['category']} | "
           f"{best_gap['Trend Status']}"
       )

       st.dataframe(
           gap_df[[
               "title",
               "category",
               "Competition",
               "Trend Status",
               "Winning Score",
               "Estimated Margin"
         ]]
     )
 else:
     st.warning("⚠️ No strong market gaps found in uploaded CSV.")

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
