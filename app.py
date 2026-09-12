import streamlit as st
from scraper_ai import fetch_and_summarize

st.set_page_config(page_title="Delhi NCR Event Scout", layout="wide", page_icon="📍")
st.title("📍 Delhi NCR Live Event Scout & Summarizer")
st.caption("Scrapes active listings across NCR and generates instant AI summaries.")

# Cache scraped events so it loads fast for your teacher
@st.cache_data(ttl=3600)
def load_data():
    return fetch_and_summarize()

with st.spinner("Fetching and summarizing Delhi NCR events..."):
    all_events = load_data()

# Search and Filter Bar
col_search, col_reg, col_cat = st.columns([2, 1, 1])

with col_search:
    query = st.text_input("🔍 Search events", placeholder="Search by name, artist, venue...")
with col_reg:
    regions = ["All NCR"] + sorted(list({e.region for e in all_events}))
    selected_reg = st.selectbox("Filter Region", regions)
with col_cat:
    categories = ["All Categories"] + sorted(list({e.category for e in all_events}))
    selected_cat = st.selectbox("Filter Category", categories)

# Apply filters
filtered = [
    e for e in all_events
    if (selected_reg == "All NCR" or e.region == selected_reg)
    and (selected_cat == "All Categories" or e.category == selected_cat)
    and (query.lower() in e.title.lower() or query.lower() in e.venue.lower() or query.lower() in e.summary.lower())
]

st.divider()
st.write(f"**Found {len(filtered)} events**")

for ev in filtered:
    with st.container(border=True):
        left, right = st.columns([4, 1])
        with left:
            st.subheader(ev.title)
            st.write(f"🏷️ **{ev.category}**  |  📍 **{ev.venue}** ({ev.region})  |  🗓️ **{ev.schedule}**")
            st.info(f"💡 **AI Summary:** {ev.summary}")
        with right:
            st.metric("Entry", ev.price)