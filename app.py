import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from pytrends.request import TrendReq

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="ZYVRO AI - Real Market Product Intelligence",
    layout="wide"
)

# ---------------- HEADER ----------------
st.title("🔥 ZYVRO AI - Real Market Product Intelligence")
st.write(
    "Validate product ideas using real Google demand signals + "
    "AI marketer strategy 🚀"
)

st.caption(
    "Built for media buyers, D2C brands, dropshippers, "
    "and performance marketers"
)

# ---------------- INPUT ----------------
product_name = st.text_input(
    "🔍 Type Winning Product Idea",
    placeholder="e.g. hair remover, posture corrector"
)

# ---------------- REAL MARKET DATA ----------------
def fetch_google_trends(keyword):
    try:
        pytrends = TrendReq(hl="en-US", tz=330)
        pytrends.build_payload([keyword], timeframe="today 12-m", geo="IN")
        interest = pytrends.interest_over_time()

        if interest.empty:
            return None

        avg_interest = round(float(interest[keyword].mean()), 2)
        latest_interest = int(interest[keyword].iloc[-1])

        trend_status = (
            "🚀 Rising"
            if latest_interest >= avg_interest
            else "📉 Stable"
        )

        return {
            "Average Interest": avg_interest,
            "Latest Interest": latest_interest,
            "Trend Status": trend_status
        }
    except Exception:
        return None


# ---------------- SCORING ENGINE ----------------
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

    scale_score = (
        wow * 0.25 +
        problem * 0.25 +
        impulse * 0.20 +
        hook * 0.20
    ) * 10

    return wow, problem, impulse, hook, scale_score


def hook_angle(name):
    name = name.lower()

    if any(k in name for k in ["corrector", "massager", "patch"]):
        return "Pain-point + before/after angle"
    elif any(k in name for k in ["led", "light", "mask"]):
        return "Visual wow + scroll-stopper angle"
    elif any(k in name for k in ["pet", "baby"]):
        return "Emotional + relatable lifestyle angle"
    return "Problem-solution + impulse angle"


def generate_hooks(name, persona):
    persona_hooks = {
        "Moms": [f"Moms are obsessed with this {name} 😍"],
        "Gym Audience": [f"This {name} is changing gym routines 💪"],
        "Beauty Buyers": [f"This {name} gives salon-level results ✨"],
        "Pet Owners": [f"Pet owners swear by this {name} 🐶"],
        "Car Lovers": [f"Car lovers are obsessed with this {name} 🚗"]
    }
    return persona_hooks.get(persona, [f"Best hook for {name}"])


def generate_ugc_script(name):
    return f"""
1. Hook → I wish I found this {name} earlier
2. Problem → show struggle
3. Demo → show usage
4. Result → transformation
5. CTA → Get yours today
"""


# ---------------- MAIN ----------------
if product_name:
    trend_data = fetch_google_trends(product_name)

    wow, problem, impulse, hook, scale_score = generate_marketing_scores(product_name)
    angle = hook_angle(product_name)

    # ---------------- REAL DEMAND KPI ----------------
    st.subheader("📈 Real Market Demand Signals")

    if trend_data:
        d1, d2, d3 = st.columns(3)
        d1.metric("📊 Avg Demand", trend_data["Average Interest"])
        d2.metric("🔥 Current Demand", trend_data["Latest Interest"])
        d3.metric("🚀 Trend", trend_data["Trend Status"])
    else:
        st.warning("⚠️ Could not fetch Google Trends data.")

    # ---------------- KPI CARDS ----------------
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("✨ Wow", wow)
    c2.metric("🧩 Problem", problem)
    c3.metric("🛒 Impulse", impulse)
    c4.metric("🎥 Hook", hook)

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

    # ---------------- PERSONA HOOKS ----------------
    persona = st.selectbox(
        "🎯 Select Target Persona",
        ["Moms", "Gym Audience", "Beauty Buyers", "Pet Owners", "Car Lovers"]
    )

    hooks = generate_hooks(product_name, persona)

    st.subheader("🎬 Hook Generator")
    for hook_text in hooks:
        st.write(f"- {hook_text}")

    # ---------------- UGC SCRIPT ----------------
    st.subheader("🎥 UGC Script")
    st.code(generate_ugc_script(product_name))

    # ---------------- CAMPAIGN STRATEGY ----------------
    st.subheader("🚀 Campaign Strategy Planner")

    budget = max(scale_score * 20, 1000)
    target_cpa = round(budget * 0.12, 2)
    expected_ctr = round((wow + hook) / 2 * 0.8, 2)

    st.markdown(f"""
### 📊 Launch Blueprint
- 🎯 Cold Audience Angle: {angle}
- 🔁 Retargeting: Social proof + urgency
- 💰 Suggested Daily Budget: ₹{round(budget, 2)}
- 🎯 Target CPA: ₹{target_cpa}
- 👆 Expected CTR: {expected_ctr}%
""")

    # ---------------- OFFER ----------------
    st.subheader("💸 Offer Engineering")

    if scale_score > 80:
        offer = "Buy 2 Get 1 Free"
    elif scale_score > 60:
        offer = "20% Launch Discount"
    else:
        offer = "Free Shipping Offer"

    st.success(f"🎁 Recommended Offer: {offer}")

    # ---------------- LANDING PAGE ----------------
    st.subheader("🧲 Landing Page Copy Generator")

    headline = f"Transform Your Routine with {product_name.title()}"
    subheadline = (
        f"The easiest way to solve your problem using {product_name}."
    )
    cta = "🔥 Get Yours Before Today’s Offer Ends"

    st.markdown(f"""
**Headline:** {headline}

**Subheadline:** {subheadline}

**CTA:** {cta}
""")

    # ---------------- KPI FORECAST ----------------
    st.subheader("📊 ROAS Forecast Dashboard")

    predicted_ctr = round((wow + hook) / 2 * 0.7, 2)
    predicted_cvr = round((problem + impulse) / 2 * 0.5, 2)
    predicted_cpc = round(max(8 - (wow * 0.4), 2), 2)
    predicted_cpa = round(predicted_cpc * 10, 2)
    predicted_roas = round(max(scale_score / 20, 1.2), 2)

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("👆 CTR", f"{predicted_ctr}%")
    k2.metric("💸 CPC", f"₹{predicted_cpc}")
    k3.metric("🛒 CVR", f"{predicted_cvr}%")
    k4.metric("🎯 CPA", f"₹{predicted_cpa}")
    k5.metric("🚀 ROAS", f"{predicted_roas}x")

else:
    st.info("👆 Type a product idea above to validate with real market data.")
