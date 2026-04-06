import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from pytrends.request import TrendReq

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="ZYVRO AI - Real Winning Product Discovery",
    layout="wide"
)

# ---------------- HEADER ----------------
st.title("🔥 ZYVRO AI - Real Winning Product Discovery")
st.write(
    "Discover real rising products from Google demand signals + "
    "AI marketer strategy 🚀"
)

st.caption(
    "Built for media buyers, D2C brands, dropshippers, "
    "and performance marketers"
)

# ---------------- REAL NICHE DISCOVERY ----------------
niche_map = {
    "Beauty": [
        "hair remover",
        "led face mask",
        "ice roller",
        "blackhead remover",
        "face lifting patch"
    ],
    "Fitness": [
        "posture corrector",
        "massage gun",
        "resistance bands",
        "ab roller",
        "smart skipping rope"
    ],
    "Pet": [
        "pet hair remover",
        "auto pet feeder",
        "pet grooming brush",
        "dog water bottle",
        "cat toy laser"
    ],
    "Kitchen": [
        "vegetable chopper",
        "portable blender",
        "oil spray bottle",
        "food sealer",
        "knife sharpener"
    ],
    "Car": [
        "car vacuum cleaner",
        "scratch remover",
        "phone holder",
        "ambient led strip",
        "tire inflator"
    ]
}

selected_niche = st.selectbox(
    "🎯 Select Niche",
    list(niche_map.keys())
)

# ---------------- GOOGLE TRENDS ----------------
def fetch_trend_score(keyword):
    try:
        pytrends = TrendReq(hl="en-US", tz=330)
        pytrends.build_payload([keyword], timeframe="today 12-m", geo="IN")
        interest = pytrends.interest_over_time()

        if interest.empty:
            return 0, "📉 No Data"

        avg_interest = round(float(interest[keyword].mean()), 2)
        latest_interest = int(interest[keyword].iloc[-1])

        status = (
            "🚀 Rising"
            if latest_interest >= avg_interest
            else "📉 Stable"
        )

        return latest_interest, status
    except Exception:
        return 0, "⚠️ Error"


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
        "led", "light", "mask", "smart"
    ]):
        wow += 4
        hook += 4

    wow = min(wow, 10)
    problem = min(problem, 10)
    impulse = min(impulse, 10)
    hook = min(hook, 10)

    scale_score = (
        wow * 0.25 +
        problem * 0.25 +
        impulse * 0.20 +
        hook * 0.20
    ) * 10

    return wow, problem, impulse, hook, scale_score


def generate_ugc_script(name):
    return f"""
1. Hook → I wish I found this {name} earlier
2. Problem → show struggle
3. Demo → show usage
4. Result → transformation
5. CTA → Get yours today
"""


# ---------------- REAL PRODUCT DISCOVERY ----------------
st.subheader("📈 Top Rising Products in Selected Niche")

discovery_rows = []

for product in niche_map[selected_niche]:
    demand, trend_status = fetch_trend_score(product)
    wow, problem, impulse, hook, scale_score = generate_marketing_scores(product)

    final_score = round((demand * 0.5) + (scale_score * 0.5), 2)

    discovery_rows.append({
        "Product": product,
        "Demand Score": demand,
        "Trend": trend_status,
        "Scale Score": scale_score,
        "Final Opportunity": final_score
    })

discovery_df = pd.DataFrame(discovery_rows)
discovery_df = discovery_df.sort_values(
    "Final Opportunity",
    ascending=False
).reset_index(drop=True)

st.dataframe(discovery_df, use_container_width=True)

# ---------------- PRODUCT SELECT ----------------
product_name = st.selectbox(
    "🔥 Select Product to Launch",
    discovery_df["Product"]
)

selected_row = discovery_df[
    discovery_df["Product"] == product_name
].iloc[0]

wow, problem, impulse, hook, scale_score = generate_marketing_scores(product_name)

# ---------------- KPI ----------------
st.subheader("📊 Selected Product Intelligence")

k1, k2, k3, k4 = st.columns(4)
k1.metric("🔥 Demand", selected_row["Demand Score"])
k2.metric("📈 Trend", selected_row["Trend"])
k3.metric("🚀 Scale Score", scale_score)
k4.metric("🏆 Opportunity", selected_row["Final Opportunity"])

# ---------------- CHART ----------------
score_df = pd.DataFrame({
    "Metric": ["Wow", "Problem", "Impulse", "Hook"],
    "Score": [wow, problem, impulse, hook]
})

fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(score_df["Metric"], score_df["Score"])
ax.set_ylim(0, 10)
ax.set_title("Creative Performance Potential")
plt.tight_layout()

buf = BytesIO()
plt.savefig(buf, format="png")
st.image(buf)

# ---------------- UGC ----------------
st.subheader("🎥 UGC Script")
st.code(generate_ugc_script(product_name))

# ---------------- OFFER ----------------
st.subheader("💸 Offer Engineering")

if scale_score > 80:
    offer = "Buy 2 Get 1 Free"
elif scale_score > 60:
    offer = "20% Launch Discount"
else:
    offer = "Free Shipping Offer"

st.success(f"🎁 Recommended Offer: {offer}")

# ---------------- KPI FORECAST ----------------
st.subheader("📊 ROAS Forecast")

predicted_ctr = round((wow + hook) / 2 * 0.7, 2)
predicted_cvr = round((problem + impulse) / 2 * 0.5, 2)
predicted_cpc = round(max(8 - (wow * 0.4), 2), 2)
predicted_roas = round(max(scale_score / 20, 1.2), 2)

r1, r2, r3, r4 = st.columns(4)
r1.metric("👆 CTR", f"{predicted_ctr}%")
r2.metric("🛒 CVR", f"{predicted_cvr}%")
r3.metric("💸 CPC", f"₹{predicted_cpc}")
r4.metric("🚀 ROAS", f"{predicted_roas}x")
