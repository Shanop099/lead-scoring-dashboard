import json
import pandas as pd
import streamlit as st
import plotly.express as px

from scorer import score_all


# ----------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------

st.set_page_config(
    page_title="AI Lead Scoring Dashboard",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 AI Lead Scoring Dashboard")
st.caption("Groq-powered Real Estate Lead Prioritization")


# ----------------------------------------------------
# LOAD LEADS
# ----------------------------------------------------

@st.cache_data
def load_leads():
    with open("leads.json", "r") as f:
        return json.load(f)


raw_leads = load_leads()


# ----------------------------------------------------
# SIDEBAR
# ----------------------------------------------------

st.sidebar.title("Dashboard Controls")

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
    "Search by Name / Project"
)


# ----------------------------------------------------
# SESSION STATE
# ----------------------------------------------------

if "results" not in st.session_state:
    st.session_state.results = []


# ----------------------------------------------------
# SCORE LEADS
# ----------------------------------------------------

if score_button:

    with st.spinner("Analyzing leads using Groq..."):

        st.session_state.results = score_all(raw_leads)

    st.success("Lead scoring completed successfully!")


results = st.session_state.results


# ----------------------------------------------------
# WAIT FOR USER
# ----------------------------------------------------

if len(results) == 0:

    st.info(
        "Click **🚀 Score Leads** to analyze the provided leads."
    )

    st.stop()


# ----------------------------------------------------
# DATAFRAME
# ----------------------------------------------------

df = pd.DataFrame(results)


# ----------------------------------------------------
# SEARCH
# ----------------------------------------------------

if search:

    query = search.lower()

    df = df[
        df["name"].str.lower().str.contains(query)
        |
        df["project"].str.lower().str.contains(query)
    ]


# ----------------------------------------------------
# PRIORITY FILTER
# ----------------------------------------------------

df = df[
    df["priority"].isin(priority_filter)
]


# ----------------------------------------------------
# KPI METRICS
# ----------------------------------------------------

total_leads = len(df)

average_score = round(
    df["score"].mean(),
    1
)

high_priority = len(
    df[df["priority"] == "High"]
)

ready_to_contact = high_priority


c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Total Leads",
    total_leads
)

c2.metric(
    "Average Score",
    average_score
)

c3.metric(
    "High Priority",
    high_priority
)

c4.metric(
    "Ready To Contact",
    ready_to_contact
)

st.divider()
# ----------------------------------------------------
# SORT LEADS
# ----------------------------------------------------

df = df.sort_values(
    by="score",
    ascending=False
)

# ----------------------------------------------------
# CHARTS
# ----------------------------------------------------

left, right = st.columns(2)

with left:

    bar = px.bar(
        df,
        x="name",
        y="score",
        color="priority",
        hover_data=[
            "project",
            "phone"
        ],
        title="Lead Scores",
        text="score"
    )

    bar.update_layout(
        xaxis_title="Lead",
        yaxis_title="AI Score",
        legend_title="Priority"
    )

    st.plotly_chart(
        bar,
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

# ----------------------------------------------------
# LEAD OVERVIEW
# ----------------------------------------------------

st.subheader("📋 Lead Overview")

overview = df[
    [
        "id",
        "name",
        "phone",
        "project",
        "score",
        "priority"
    ]
]

st.dataframe(
    overview,
    use_container_width=True,
    hide_index=True
)

st.divider()

# ----------------------------------------------------
# PROJECT SUMMARY
# ----------------------------------------------------

st.subheader("🏢 Project Summary")

project_summary = (
    df.groupby("project")
      .agg(
          Leads=("id", "count"),
          AvgScore=("score", "mean")
      )
      .reset_index()
)

project_summary["AvgScore"] = (
    project_summary["AvgScore"]
    .round(1)
)

st.dataframe(
    project_summary,
    use_container_width=True,
    hide_index=True
)

st.divider()

# ----------------------------------------------------
# DUPLICATE PHONE CHECK
# ----------------------------------------------------

duplicates = (
    df.groupby("phone")
      .size()
      .reset_index(name="count")
)

duplicates = duplicates[
    duplicates["count"] > 1
]

if len(duplicates):

    st.warning("⚠ Duplicate phone numbers detected.")

    duplicate_df = (
        df[df["phone"].isin(duplicates["phone"])]
        .sort_values("phone")
    )

    st.dataframe(
        duplicate_df[
            [
                "name",
                "phone",
                "project",
                "score"
            ]
        ],
        hide_index=True,
        use_container_width=True
    )

else:

    st.success(
        "No duplicate phone numbers found."
    )

st.divider()

st.subheader("🤖 AI Lead Analysis")
# ----------------------------------------------------
# LEAD DETAILS
# ----------------------------------------------------

priority_badges = {
    "High": "🟢 High Priority",
    "Medium": "🟡 Medium Priority",
    "Low": "🔴 Low Priority"
}

for _, lead in df.iterrows():

    title = (
        f"{lead['name']} • "
        f"{lead['project']} "
        f"({lead['score']}/100)"
    )

    with st.expander(title):

        left, right = st.columns([2, 1])

        # ----------------------------------
        # Lead Information
        # ----------------------------------

        with left:

            st.markdown("### 👤 Lead Information")

            st.write(f"**Lead ID:** {lead['id']}")
            st.write(f"**Name:** {lead['name']}")
            st.write(f"**Phone:** {lead['phone']}")
            st.write(f"**Project:** {lead['project']}")

            st.markdown("### 💬 Customer Message")

            message = str(lead.get("message", "")).strip()

            if message:
                st.info(message)
            else:
                st.warning("No message provided.")

        # ----------------------------------
        # Score Section
        # ----------------------------------

        with right:

            st.metric(
                "Lead Score",
                f"{lead['score']}/100"
            )

            st.progress(
                int(lead["score"])
            )

            st.write(
                priority_badges.get(
                    lead["priority"],
                    lead["priority"]
                )
            )

        st.markdown("---")

        # ----------------------------------
        # AI Reasoning
        # ----------------------------------

        st.markdown("### 🧠 AI Reasoning")

        reasons = lead.get("reason", [])

        if isinstance(reasons, list):

            for reason in reasons:
                st.write(f"✅ {reason}")

        elif reasons:
            st.write(reasons)

        else:
            st.write("No reasoning available.")

        st.markdown("### 📞 Recommended Next Action")

        st.success(
            lead.get(
                "next_action",
                "No recommendation available."
            )
        )

        # ----------------------------------
        # Duplicate Detection
        # ----------------------------------

        duplicate_count = len(
            df[df["phone"] == lead["phone"]]
        )

        if duplicate_count > 1:

            st.warning(
                f"⚠ Duplicate enquiry detected.\n\n"
                f"This phone number appears "
                f"{duplicate_count} times."
            )

            duplicates = df[
                df["phone"] == lead["phone"]
            ][
                [
                    "name",
                    "project",
                    "score",
                    "priority"
                ]
            ]

            st.dataframe(
                duplicates,
                use_container_width=True,
                hide_index=True
            )

        st.divider()

        # ----------------------------------------------------
# AI INSIGHTS
# ----------------------------------------------------

st.header("📊 AI Insights")

c1, c2 = st.columns(2)

# ----------------------------------------------------
# HIGH PRIORITY
# ----------------------------------------------------

with c1:

    st.subheader("🟢 High Priority Leads")

    high_df = df[
        df["priority"] == "High"
    ]

    if len(high_df):

        for _, row in high_df.iterrows():

            st.success(
                f"""
**{row['name']}**

📞 {row['phone']}

🏠 {row['project']}

⭐ Score : {row['score']}
"""
            )

    else:

        st.info(
            "No High Priority Leads."
        )

# ----------------------------------------------------
# LOW PRIORITY
# ----------------------------------------------------

with c2:

    st.subheader("🔴 Low Priority Leads")

    low_df = df[
        df["priority"] == "Low"
    ]

    if len(low_df):

        for _, row in low_df.iterrows():

            st.warning(
                f"""
**{row['name']}**

📞 {row['phone']}

🏠 {row['project']}

⭐ Score : {row['score']}
"""
            )

    else:

        st.info(
            "No Low Priority Leads."
        )

st.divider()

# ----------------------------------------------------
# PROJECT ANALYTICS
# ----------------------------------------------------

st.header("🏢 Project Analytics")

project_stats = (
    df.groupby("project")
    .agg(
        Total_Leads=("id", "count"),
        Average_Score=("score", "mean")
    )
    .reset_index()
)

project_stats["Average_Score"] = (
    project_stats["Average_Score"]
    .round(1)
)

st.dataframe(
    project_stats,
    hide_index=True,
    use_container_width=True
)

fig = px.bar(
    project_stats,
    x="project",
    y="Average_Score",
    text="Average_Score",
    title="Average Lead Score per Project"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()

# ----------------------------------------------------
# OVERALL AI SUMMARY
# ----------------------------------------------------

st.header("🧠 AI Summary")

highest = df.loc[df["score"].idxmax()]
lowest = df.loc[df["score"].idxmin()]

left, right = st.columns(2)

with left:

    st.info(
        f"""
### Highest Quality Lead

**Name:** {highest['name']}

**Project:** {highest['project']}

**Score:** {highest['score']}

**Priority:** {highest['priority']}
"""
    )

with right:

    st.warning(
        f"""
### Lowest Quality Lead

**Name:** {lowest['name']}

**Project:** {lowest['project']}

**Score:** {lowest['score']}

**Priority:** {lowest['priority']}
"""
    )

st.divider()
# ----------------------------------------------------
# DOWNLOAD RESULTS
# ----------------------------------------------------

st.header("📥 Export Results")

export_df = df.copy()

# Convert AI reasons list into readable text
if "reason" in export_df.columns:
    export_df["reason"] = export_df["reason"].apply(
        lambda x: ", ".join(x) if isinstance(x, list) else str(x)
    )

csv = export_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇ Download Scored Leads (CSV)",
    data=csv,
    file_name="scored_leads.csv",
    mime="text/csv",
    use_container_width=True,
)

st.divider()

# ----------------------------------------------------
# DASHBOARD SUMMARY
# ----------------------------------------------------

st.header("📈 Dashboard Summary")

high_count = len(df[df["priority"] == "High"])
medium_count = len(df[df["priority"] == "Medium"])
low_count = len(df[df["priority"] == "Low"])

summary = f"""
### AI Analysis Completed

Total Leads Analyzed : **{len(df)}**

🟢 High Priority : **{high_count}**

🟡 Medium Priority : **{medium_count}**

🔴 Low Priority : **{low_count}**

Average Lead Score : **{round(df['score'].mean(),1)} / 100**
"""

st.markdown(summary)

st.divider()

# ----------------------------------------------------
# FOOTER
# ----------------------------------------------------

st.markdown(
    """
---
### 🚀 About this Dashboard

This dashboard uses **Groq LLM** to intelligently analyze real estate enquiries
and assign a lead score based on:

- Customer buying intent
- Urgency
- Message quality
- Conversion potential

Features Included:

- ✅ AI Lead Scoring
- ✅ Priority Classification
- ✅ Duplicate Phone Detection
- ✅ AI Recommendations
- ✅ Interactive Charts
- ✅ Project-wise Analytics
- ✅ CSV Export
"""
)

st.caption(
    "Built with ❤️ using Streamlit + Groq"
)