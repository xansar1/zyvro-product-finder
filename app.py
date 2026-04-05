import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="ZYVRO AI - Winning Product Validator",
    layout="wide"
)

# ---------------- HEADER ----------------
st.title("🔥 ZYVRO AI - Winning Product Validator")
st.write(
    "Type a product name and instantly validate "
    "Meta ads scaling potential 🚀"
)

st.caption(
    "Built for media buyers, D2C brands, dropshippers, "
    "and performance marketers"
)

# ---------------- INPUT ----------------
product_name = st.text_input(
    "🔍 Type Winning Product Idea",
    placeholder="e.g. posture corrector, pet hair remover"
)

# ---------------- SCORING ENGINE ----------------
def generate_marketing_scores(name):
    name = name.lower()

    wow = 5
    problem = 5
    impulse = 5
    hook = 5

    # Problem-solver products
    if any(k in name for k in [
        "corrector", "remover", "cleaner",
        "massager", "patch", "repair"
    ]):
        problem += 4
        impulse += 2

    # Visual wow products
    if any(k in name for k in [
        "led", "light", "mask", "smart",
        "rgb", "projector"
    ]):
        wow += 4
        hook += 4

    # Viral lifestyle products
    if any(k in name for k in [
        "pet", "baby", "kitchen",
        "fitness", "beauty", "car"
    ]):
        problem += 2
        hook += 2

    # Clamp max
    wow = min(wow, 10)
    problem = min(problem, 10)
    impulse = min(impulse, 10)
    hook = min(hook, 10)

    scale_score = (
        wow * 0.30 +
        problem * 0.30 +
        impulse * 0.20 +
        hook * 0.20
    ) * 10

    return wow, problem, impulse, hook, scale_score


def scale_label(score):
    if score > 80:
        return "🔥 High Meta Ads Potential"
    elif score > 60:
        return "🚀 Strong Test Product"
    return "⚠️ Weak Creative Product"


def hook_angle(name):
    name = name.lower()

    if any(k in name for k in ["corrector", "massager", "patch"]):
        return "Pain-point + before/after angle"
    elif any(k in name for k in ["led", "light", "mask"]):
        return "Visual wow + scroll-stopper angle"
    elif any(k in name for k in ["pet", "baby"]):
        return "Emotional + relatable lifestyle angle"
    return "Problem-solution + impulse angle"


# ---------------- MAIN ----------------
if product_name:
    wow, problem, impulse, hook, scale_score = generate_marketing_scores(product_name)
    label = scale_label(scale_score)
    angle = hook_angle(product_name)

    # ---------------- TOP RESULT ----------------
    st.success(
        f"🚀 {product_name} → {label} | "
        f"Scale Score: {round(scale_score, 2)}"
    )

    # ---------------- KPI CARDS ----------------
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("✨ Wow Factor", wow)
    c2.metric("🧩 Problem Solving", problem)
    c3.metric("🛒 Impulse Buy", impulse)
    c4.metric("🎥 Visual Hook", hook)

    # ---------------- SCORE TABLE ----------------
    score_df = pd.DataFrame({
        "Metric": [
            "Wow Factor",
            "Problem Solving",
            "Impulse Buy",
            "Visual Hook"
        ],
        "Score": [wow, problem, impulse, hook]
    })

    st.subheader("📊 Product Marketing Breakdown")
    st.dataframe(score_df, use_container_width=True)

    # ---------------- CHART ----------------
    st.subheader("📈 Creative Scaling Breakdown")

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(score_df["Metric"], score_df["Score"])
    ax.set_ylim(0, 10)
    ax.set_title("Creative Performance Potential")
    plt.xticks(rotation=20)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format="png")
    st.image(buf)

    # ---------------- STRATEGIC INSIGHT ----------------
    st.subheader("🎯 Marketer Insight")
    st.info(f"📢 Best Hook Angle: **{angle}**")

    if scale_score > 80:
        st.success(
            "This is highly scalable for Meta/TikTok ads. "
            "Focus on short-form UGC creatives and strong hooks."
        )
    elif scale_score > 60:
        st.warning(
            "Good testing product. Creative execution quality "
            "will decide profitability."
        )
    else:
        st.error(
            "Weak ad potential. Harder to stop scroll "
            "or generate strong CTR."
        )

else:
    st.info("👆 Type a product idea above to validate its ad potential.")
