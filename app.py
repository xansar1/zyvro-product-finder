import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from pytrends.request import TrendReq

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="ZYVRO AI - Real Product Discovery Engine",
    layout="wide"
)

# ---------------- HEADER ----------------
st.title("🔥 ZYVRO AI - Real Product Discovery Engine")
st.write(
    "Discover 100+ real rising products from Google demand signals + "
    "AI marketer strategy 🚀"
)

st.caption(
    "Built for D2C brands, media buyers, dropshippers, "
    "performance marketers, and ecommerce founders"
)

# ---------------- INPUT ----------------
niche = st.text_input(
    "🎯 Enter Niche",
    placeholder="beauty, fitness, pet, kitchen, car"
)

# ---------------- REAL COLLECTION ----------------
def fetch_related_products(keyword):
    try:
        pytrends = TrendReq(hl="en-US", tz=330)
        pytrends.build_payload([keyword], timeframe="today 12-m", geo="IN")

        related = pytrends.related_queries()

        if keyword not in related:
            return []

        rising = related[keyword]["rising"]
        top = related[keyword]["top"]

        final_products = []

        if rising is not None:
            final_products.extend(rising["query"].tolist())

        if top is not None:
            final_products.extend(top["query"].tolist())

        # remove duplicates
        final_products = list(dict.fromkeys(final_products))
        return final_products[:100]

    except Exception:
        return []


# ---------------- MARKETING ENGINE ----------------
def generate_marketing_scores(name):
    name = name.lower()

    wow = 5
    problem = 5
    impulse = 5
    hook = 5

    if any(k in name for k in [
        "corrector", "remover", "cleaner",
        "massager", "patch", "repair"
    ]):
        problem += 4
        impulse += 2

    if any(k in name for k in [
        "led", "light", "mask", "smart",
        "rgb", "projector"
    ]):
        wow += 4
        hook += 4

    if any(k in name for k in [
        "pet", "baby", "kitchen",
        "fitness", "beauty", "car"
    ]):
        problem += 2
        hook += 2

    wow = min(wow, 10)
    problem = min(problem, 10)
    impulse = min(impulse, 10)
    hook = min(hook, 10)

    score = (
        wow * 0.30 +
        problem * 0.30 +
        impulse * 0.20 +
        hook * 0.20
    ) * 10

    return wow, problem, impulse, hook, round(score, 2)


def trend_label(score):
    if score > 80:
        return "🚀 Breakout"
    elif score > 60:
        return "📈 Rising"
    return "📉 Stable"


def offer_engine(score):
    if score > 80:
        return "Buy 2 Get 1 Free"
    elif score > 60:
        return "20% Launch Discount"
    return "Free Shipping Offer"


# ---------------- MAIN ----------------
if niche:
    products = fetch_related_products(niche)

    if products:
        discovery_rows = []

        for product in products:
            wow, problem, impulse, hook, scale_score = generate_marketing_scores(product)

            discovery_rows.append({
                "Product": product,
                "Wow": wow,
                "Problem": problem,
                "Impulse": impulse,
                "Hook": hook,
                "Scale Score": scale_score,
                "Trend": trend_label(scale_score)
            })

        df = pd.DataFrame(discovery_rows)
        df = df.sort_values(
            "Scale Score",
            ascending=False
        ).reset_index(drop=True)

        st.success(f"🔥 Found {len(df)} real products from live Google demand")

        # ---------------- TABLE ----------------
        st.subheader("📊 Real Product Opportunity Table")
        st.dataframe(df, use_container_width=True)

        # ---------------- PRODUCT SELECT ----------------
        selected_product = st.selectbox(
            "🚀 Select Product to Launch",
            df["Product"]
        )

        selected_row = df[df["Product"] == selected_product].iloc[0]

        # ---------------- KPI ----------------
        st.subheader("📈 Product Intelligence")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("✨ Wow", selected_row["Wow"])
        c2.metric("🧩 Problem", selected_row["Problem"])
        c3.metric("🛒 Impulse", selected_row["Impulse"])
        c4.metric("🎥 Hook", selected_row["Hook"])

        # ---------------- CHART ----------------
        score_df = pd.DataFrame({
            "Metric": ["Wow", "Problem", "Impulse", "Hook"],
            "Score": [
                selected_row["Wow"],
                selected_row["Problem"],
                selected_row["Impulse"],
                selected_row["Hook"]
            ]
        })

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(score_df["Metric"], score_df["Score"])
        ax.set_ylim(0, 10)
        ax.set_title("Creative Performance Potential")
        plt.tight_layout()

        buf = BytesIO()
        plt.savefig(buf, format="png")
        st.image(buf)

        # ---------------- STRATEGY ----------------
        st.subheader("🚀 Launch Strategy")
        st.success(
            f"📈 {selected_product} → {selected_row['Trend']} | "
            f"Scale Score: {selected_row['Scale Score']}"
        )

        # ---------------- OFFER ----------------
        offer = offer_engine(selected_row["Scale Score"])
        st.subheader("💸 Offer Engineering")
        st.success(f"🎁 Recommended Offer: {offer}")

        # ---------------- KPI FORECAST ----------------
        st.subheader("📊 KPI Forecast")

        predicted_ctr = round(
            (selected_row["Wow"] + selected_row["Hook"]) / 2 * 0.7, 2
        )
        predicted_cvr = round(
            (selected_row["Problem"] + selected_row["Impulse"]) / 2 * 0.5, 2
        )
        predicted_roas = round(
            max(selected_row["Scale Score"] / 20, 1.2), 2
        )

        k1, k2, k3 = st.columns(3)
        k1.metric("👆 CTR", f"{predicted_ctr}%")
        k2.metric("🛒 CVR", f"{predicted_cvr}%")
        k3.metric("🚀 ROAS", f"{predicted_roas}x")

        # ---------------- CSV EXPORT ----------------
        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "📥 Download Real Product Research CSV",
            data=csv,
            file_name=f"{niche}_real_product_research.csv",
            mime="text/csv"
        )

    else:
        st.warning("⚠️ No real products found for this niche.")

else:
    st.info("👆 Enter a niche to discover 100+ real winning products.")
