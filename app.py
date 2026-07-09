import json
import pandas as pd
import streamlit as st
import plotly.express as px

from scorer import score_all


# -----------------------------
# Page Config
# -----------------------------

st.set_page_config(
    page_title="AI Lead Scoring Dashboard",
    page_icon="📈",
    layout="wide"
)


st.title("📈 AI Lead Scoring Dashboard")
st.caption("Lead Prioritization using Groq LLM")


# -----------------------------
# Load Leads
# -----------------------------

@st.cache_data
def load_leads():

    with open("leads.json", "r") as f:
        return json.load(f)


raw_leads = load_leads()


# -----------------------------
# Sidebar
# -----------------------------

st.sidebar.header("Controls")

score_button = st.sidebar.button(
    "🚀 Score Leads",
    use_container_width=True
)

priority_filter = st.sidebar.multiselect(
    "Priority",
    ["High", "Medium", "Low"],
    default=["High", "Medium", "Low"]
)

search = st.sidebar.text_input(
    "Search Company / Person"
)


# -----------------------------
# Session State
# -----------------------------

if "results" not in st.session_state:
    st.session_state.results = []


# -----------------------------
# AI Scoring
# -----------------------------

if score_button:

    with st.spinner("Groq is evaluating leads..."):

        st.session_state.results = score_all(raw_leads)

        st.success("Lead scoring completed!")


results = st.session_state.results


# -----------------------------
# No Results
# -----------------------------

if len(results) == 0:

    st.info("Press **Score Leads** to begin.")

    st.stop()


# -----------------------------
# DataFrame
# -----------------------------

df = pd.DataFrame(results)


# -----------------------------
# Search
# -----------------------------

if search:

    search = search.lower()

    df = df[
        df["name"].str.lower().str.contains(search)
        |
        df["company"].str.lower().str.contains(search)
    ]


# -----------------------------
# Priority Filter
# -----------------------------

df = df[df["priority"].isin(priority_filter)]


# -----------------------------
# Metrics
# -----------------------------

total = len(df)

average = round(df["score"].mean(), 1)

high = len(df[df["priority"] == "High"])

pipeline = int(df["budget"].sum())


c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Total Leads",
    total
)

c2.metric(
    "Average Score",
    average
)

c3.metric(
    "High Priority",
    high
)

c4.metric(
    "Pipeline Budget",
    f"${pipeline:,}"
)


st.divider()


# -----------------------------
# Charts
# -----------------------------

left, right = st.columns(2)


with left:

    fig = px.bar(
        df,
        x="company",
        y="score",
        color="priority",
        title="Lead Scores"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


with right:

    pie = px.pie(
        df,
        names="priority",
        title="Priority Distribution"
    )

    st.plotly_chart(
        pie,
        use_container_width=True
    )


st.divider()


# -----------------------------
# Table
# -----------------------------

st.subheader("Lead Overview")

table = df[
    [
        "name",
        "company",
        "designation",
        "score",
        "priority",
        "budget"
    ]
].sort_values(
    "score",
    ascending=False
)

st.dataframe(
    table,
    use_container_width=True,
    hide_index=True
)


st.divider()

st.subheader("Lead Details")
# -----------------------------
# Lead Details
# -----------------------------

priority_colors = {
    "High": "🟢",
    "Medium": "🟡",
    "Low": "🔴",
    "Unknown": "⚪"
}

for _, lead in df.sort_values("score", ascending=False).iterrows():

    color = priority_colors.get(
        lead["priority"],
        "⚪"
    )

    title = (
        f"{color} "
        f"{lead['name']} "
        f"— {lead['company']} "
        f"({lead['score']}/100)"
    )

    with st.expander(title):

        left, right = st.columns([2, 1])

        with left:

            st.markdown("### Company")

            st.write(f"**Company:** {lead['company']}")
            st.write(f"**Industry:** {lead['industry']}")
            st.write(f"**Location:** {lead['location']}")
            st.write(f"**Employees:** {lead['employees']}")
            st.write(f"**Revenue:** {lead['annual_revenue']}")

            st.markdown("### Contact")

            st.write(f"**Name:** {lead['name']}")
            st.write(f"**Designation:** {lead['designation']}")

            st.markdown("### Opportunity")

            st.write(f"**Budget:** ${lead['budget']:,}")
            st.write(f"**Timeline:** {lead['timeline']}")
            st.write(f"**Engagement:** {lead['engagement']}")

        with right:

            st.metric(
                "Lead Score",
                f"{lead['score']}/100"
            )

            st.progress(
                int(lead["score"])
            )

            st.metric(
                "Priority",
                lead["priority"]
            )

        st.markdown("---")

        st.markdown("### 🤖 AI Reasoning")

        reasons = lead.get("reason", [])

        if isinstance(reasons, list):

            for item in reasons:
                st.write(f"• {item}")

        else:
            st.write(reasons)

        st.markdown("### 🎯 Recommended Next Action")

        st.success(
            lead.get(
                "next_action",
                "No recommendation available."
            )
        )

        st.markdown("---")


# -----------------------------
# Footer
# -----------------------------

st.divider()

st.caption(
    "Built with ❤️ using Streamlit + Groq Llama 3.3 70B"
)