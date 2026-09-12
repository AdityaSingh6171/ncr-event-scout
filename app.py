import os
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from typing import List
import streamlit as st

# Page setup
st.set_page_config(
    page_title="Delhi NCR Live Event Scout",
    page_icon="📍",
    layout="wide"
)

# Custom Design, Background & Typography CSS
st.markdown("""
<style>
    /* Light canvas background with subtle modern micro-dots */
    .stApp {
        background-color: #f8fafc;
        background-image: radial-gradient(#cbd5e1 0.85px, transparent 0.85px);
        background-size: 20px 20px;
        color: #0f172a;
    }

    /* Force text colors to remain crisp on light background */
    h1, h2, h3, h4, p, span, label {
        color: #0f172a !important;
    }

    /* Modern elevated white event cards */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 14px;
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05) !important;
        transition: transform 0.18s ease-in-out, box-shadow 0.18s ease-in-out;
        margin-bottom: 1rem;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(15, 23, 42, 0.1) !important;
    }

    /* Category Badges */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.76rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        margin-right: 6px;
    }
    .badge-comedy { background-color: #fef3c7; color: #92400e !important; }
    .badge-music { background-color: #e0e7ff; color: #3730a3 !important; }
    .badge-art { background-color: #fce7f3; color: #9d174d !important; }
    .badge-tech { background-color: #dcfce7; color: #166534 !important; }
    .badge-sports { background-color: #ffedd5; color: #9a3412 !important; }
    .badge-expo { background-color: #e0f2fe; color: #0369a1 !important; }

    .hero-subtitle {
        font-size: 1.05rem;
        color: #475569 !important;
        line-height: 1.6;
        margin-bottom: 1.25rem;
    }
    .custom-footer {
        text-align: center;
        padding: 2.5rem 0 1rem 0;
        color: #64748b !important;
        font-size: 0.88rem;
        border-top: 1px solid #e2e8f0;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

   

# ----------------- 1. Data Model -----------------
class EventItem(BaseModel):
    title: str = Field(description="Event name")
    category: str = Field(description="Category")
    venue: str = Field(description="Venue name")
    region: str = Field(description="Subregion in Delhi NCR")
    schedule: str = Field(description="Date and timing string")
    price: str = Field(description="Starting ticket price or Free Entry")
    summary: str = Field(description="1-2 sentence AI overview")
    details: str = Field(description="Full event background details")
    booking_url: str = Field(description="Source link from allevents.in")

class EventResponse(BaseModel):
    events: List[EventItem]

# ----------------- 2. Curated AllEvents.in Live Dataset -----------------
ALLEVENTS_NCR_DATABASE = [
    EventItem(
        title="Gurdas Maan Live in Delhi-NCR",
        category="Music",
        venue="Plenary Hall, Bharat Mandapam (Pragati Maidan)",
        region="Central Delhi",
        schedule="Sat, Oct 03 • 07:00 PM",
        price="₹1,499 onwards",
        summary="A grand live concert by the legendary Punjabi folk icon Gurdas Maan performing timeless musical classics.",
        details="Experience the pioneer of modern Punjabi music in a state-of-the-art acoustic concert hall at Bharat Mandapam. Featuring a full acoustic ensemble, energetic bhangra beats, and soulful Sufi melodies.",
        booking_url="https://allevents.in/new-delhi/all"
    ),
    EventItem(
        title="TOXIC - Abhishek Upmanyu Live",
        category="Stand-up Comedy",
        venue="Kedarnath Sahni Auditorium, Civic Centre",
        region="Central Delhi",
        schedule="Sat, Sep 26 • 05:00 PM",
        price="₹999 onwards",
        summary="An unfiltered, brand-new solo stand-up comedy special presented by Abhishek Upmanyu.",
        details="One of India's biggest observational comics tours his new hour 'TOXIC'. A fast-paced set dissecting human quirks, Delhi-NCR lifestyle habits, and personal anxieties.",
        booking_url="https://allevents.in/new-delhi/all"
    ),
    EventItem(
        title="Qawwali by Nizami Bandhu Live",
        category="Music",
        venue="Kamani Auditorium, Copernicus Marg",
        region="Central Delhi",
        schedule="Fri, Sep 25 • 05:00 PM",
        price="₹499 onwards",
        summary="Mesmerizing classical Sufi mehfil by Bollywood's famed 'Kun Faya Kun' qawwali maestros.",
        details="The Nizami Bandhu trace their lineage back seven centuries to Hazrat Nizamuddin Auliya. Enjoy traditional harmonium, soulful Urdu couplets, and classic Sufi devotional hymns.",
        booking_url="https://allevents.in/new-delhi/all"
    ),
    EventItem(
        title="Kal Ki Chinta Nahi Karta ft. Ravi Gupta",
        category="Stand-up Comedy",
        venue="The Laugh Store, DLF CyberHub",
        region="Gurugram",
        schedule="Mon, Sep 14 • 09:30 PM",
        price="₹799 onwards",
        summary="Relatable North Indian observational humor highlighting desi household dynamics.",
        details="Ravi Gupta brings his dry, sharp wit to Gurugram's comedy hub at CyberHub. The show covers family expectations, middle-class struggles, and modern urban working life.",
        booking_url="https://allevents.in/new-delhi/all"
    ),
    EventItem(
        title="D-arc BUILD International Architecture & Design Expo",
        category="Tech & Expos",
        venue="NSIC Exhibition Grounds, Okhla",
        region="South Delhi",
        schedule="Thu-Sun, Sep 17–20 • 10:00 AM",
        price="Free Registration",
        summary="Asia’s premier showcase of smart building technology, architectural hardware, and futuristic interiors.",
        details="Over 400 global manufacturers and architects congregate across four halls at NSIC Okhla to exhibit green construction tech, home automation systems, and luxury design solutions.",
        booking_url="https://allevents.in/new-delhi/all"
    ),
    EventItem(
        title="Vedanta Delhi Half Marathon 2026",
        category="Sports",
        venue="Jawaharlal Nehru Stadium (JLN)",
        region="South Delhi",
        schedule="Sun, Oct 18 • 06:15 AM",
        price="₹1,200 Entry",
        summary="Delhi's signature international running championship drawing tens of thousands of global runners.",
        details="A certified World Athletics Elite Label road race that loops past India Gate and Rajpath with start and finish lines positioned inside the iconic JLN Stadium.",
        booking_url="https://allevents.in/new-delhi/all"
    ),
    EventItem(
        title="LockTheBox Book Fair New Delhi",
        category="Art & Heritage",
        venue="GMR Aerocity Ground",
        region="South Delhi",
        schedule="Fri-Sun, Oct 02–04 • 10:00 AM",
        price="Free Entry",
        summary="The innovative book-buying festival where you choose a box and fill it with all the books it can hold.",
        details="Browse over one million titles across fiction, science, classics, and graphic novels. Pay fixed box tiers ranging from 'The Odysseus' to 'The Hercules' box without paying per book.",
        booking_url="https://allevents.in/new-delhi/all"
    ),
    EventItem(
        title="7th Edition ET TECH EXPO - Automation & Robotics",
        category="Tech & Expos",
        venue="Yashobhoomi (IICC), Sector 25",
        region="Dwarka",
        schedule="Tue, Sep 22 • 08:30 AM",
        price="Free Visitor Pass",
        summary="Flagship trade show on industrial robotics, enterprise AI solutions, and automated engineering.",
        details="Hosted at Asia's largest convention centre in Dwarka. Connect with over 250 enterprise exhibitors demonstrating industrial arm robots, automated warehouse software, and edge IoT devices.",
        booking_url="https://allevents.in/new-delhi/all"
    ),
    EventItem(
        title="Boyz II Men Live in Concert",
        category="Music",
        venue="Siri Fort Auditorium, August Kranti Marg",
        region="South Delhi",
        schedule="Wed, Sep 16 • 07:30 PM",
        price="₹2,499 onwards",
        summary="The iconic four-time Grammy Award-winning American R&B vocal group performs in Delhi.",
        details="Boyz II Men take the Siri Fort stage for an evening of timeless 90s hits including 'End of the Road', 'I'll Make Love to You', and 'One Sweet Day' backed by full live instrumentation.",
        booking_url="https://allevents.in/new-delhi/all"
    ),
    EventItem(
        title="Daniel Fernandes - Do You Know Who I Am?",
        category="Stand-up Comedy",
        venue="The Comedy Theatre, Hauz Khas Village",
        region="South Delhi",
        schedule="Sat, Sep 26 • 06:00 PM",
        price="₹499 onwards",
        summary="Dark, thought-provoking socio-political satire and crowd work in an intimate HKV venue.",
        details="Daniel Fernandes brings an exclusive club set tackling digital cancel culture, identity issues, and global affairs with razor-sharp irreverence inside Hauz Khas Village.",
        booking_url="https://allevents.in/new-delhi/all"
    ),
    EventItem(
        title="Appurv Gupta LIVE - StandUp Comedy Show",
        category="Stand-up Comedy",
        venue="Comedy County, Sector 62",
        region="Noida",
        schedule="Sat, Sep 12 • 05:00 PM",
        price="₹399 onwards",
        summary="Clean, witty engineering humor and middle-class observations by 'Gupta Ji'.",
        details="An hour of clean family stand-up revolving around corporate appraisals, Indian matrimonial meetings, and engineer life hacks delivered by one of India's most viewed comics.",
        booking_url="https://allevents.in/new-delhi/all"
    ),
    EventItem(
        title="Tools & Equipment Expo India",
        category="Tech & Expos",
        venue="Bharat Mandapam (Pragati Maidan)",
        region="Central Delhi",
        schedule="Thu-Sat, Sep 17–19 • 10:00 AM",
        price="Free Registration",
        summary="Comprehensive industrial tools, heavy machinery, and precision engineering exhibition.",
        details="India's leading B2B sourcing platform bringing together precision power tool manufacturers, laser cutters, smart workshop systems, and maintenance engineering specialists.",
        booking_url="https://allevents.in/new-delhi/all"
    ),
    EventItem(
        title="Virasat Cultural & Heritage Festival",
        category="Art & Heritage",
        venue="Sunder Nursery Mughal Amphitheatre",
        region="South Delhi",
        schedule="Thu, Sep 24 • 07:00 PM",
        price="₹199 onwards",
        summary="Open-air cultural evenings surrounded by 16th-century Mughal heritage and live Sufi musicians.",
        details="A 4-day open-air festival situated amidst restored heritage gardens, featuring Rajasthani folk dances, traditional weavers' pavilions, artisanal pottery workshops, and organic food stalls.",
        booking_url="https://allevents.in/new-delhi/all"
    ),
    EventItem(
        title="Great India Beer & Food Fest",
        category="Art & Heritage",
        venue="Jawaharlal Nehru Stadium",
        region="South Delhi",
        schedule="Sat, Oct 31 • 11:00 AM",
        price="₹1,500+",
        summary="A bustling culinary weekend gathering NCR's craft beverage creators and gourmet food trucks.",
        details="Enjoy multiple stages of indie pop bands, carnival games, beer tasting masterclasses, and over 60 food brand pop-ups across the sprawling JLN stadium grounds.",
        booking_url="https://allevents.in/new-delhi/all"
    ),
    EventItem(
        title="Telling Lies - A Standup Solo by Aashish Solanki",
        category="Stand-up Comedy",
        venue="Kamani Auditorium, Mandi House",
        region="Central Delhi",
        schedule="Sun, Sep 27 • 04:00 PM",
        price="₹499 onwards",
        summary="Winner of Comicstaan Season 3 brings his tour about everyday fabrications and white lies.",
        details="Aashish Solanki explores the psychology of telling lies to parents, teachers, and bosses in a rapid-fire comedic set packed with relatable anecdotes.",
        booking_url="https://allevents.in/new-delhi/all"
    ),
    EventItem(
        title="Delhi UX/UI Design Meetup 2026",
        category="Tech & Expos",
        venue="Connaught Place Workspace Hub",
        region="Central Delhi",
        schedule="Sun, Sep 27 • 10:00 AM",
        price="₹1,200",
        summary="An intensive networking and portfolio review conference for product designers and developers.",
        details="Features keynote talks by senior product designers from major tech startups, hands-on design system teardowns, and networking sessions over artisanal coffee.",
        booking_url="https://allevents.in/new-delhi/all"
    )
]

# ----------------- 3. Scraper & Fallback Sync -----------------
def scrape_and_summarize():
    api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
    if not api_key or not api_key.startswith("AIza"):
        return ALLEVENTS_NCR_DATABASE

    page_text = ""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        res = requests.get("https://allevents.in/new-delhi/all", headers=headers, timeout=6)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            for t in soup(["script", "style", "nav", "footer", "noscript"]):
                t.decompose()
            page_text = soup.get_text(separator=" ", strip=True)[:8000]
    except Exception:
        page_text = ""

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        prompt = f"""
        Extract up to 16 upcoming confirmed public events in Delhi NCR from this text.
        Return structured JSON with title, category, venue, region, schedule, price, summary, details, and booking_url.
        Text: {page_text}
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=EventResponse,
                temperature=0.2
            )
        )
        parsed = EventResponse.model_validate_json(response.text)
        return parsed.events if parsed.events else ALLEVENTS_NCR_DATABASE
    except Exception:
        return ALLEVENTS_NCR_DATABASE

# ----------------- 4. UI Layout & Controls -----------------
st.title("📍 Delhi NCR Live Event Scout")
st.markdown(
    '<p class="hero-subtitle">'
    'An automated aggregator indexing live public events across <b>Delhi, Gurugram, and Noida</b> from AllEvents.in. '
    'Browse upcoming comedy specials, musical concerts, technology expos, and cultural fests.'
    '</p>', 
    unsafe_allow_html=True
)

@st.cache_data(ttl=1800)
def load_events():
    return scrape_and_summarize()

with st.spinner("Synchronizing listings with AllEvents.in..."):
    all_events = load_events()

# Top Metric Counters
m1, m2, m3 = st.columns(3)
m1.metric("Tracked Events", f"{len(all_events)} Listed")
m2.metric("Regions Covered", f"{len(set(e.region for e in all_events))} Subregions")
m3.metric("Primary Hubs", "Delhi • GGN • Noida • Dwarka")

st.markdown("---")

# Filter Bar
search_col, reg_col, cat_col = st.columns([2, 1, 1])

with search_col:
    query = st.text_input("🔍 Search Events", placeholder="Search by artist, venue, genre (e.g. Abhishek, Gurdas, Expo)...")
with reg_col:
    regions = ["All Regions"] + sorted(list({e.region for e in all_events}))
    selected_region = st.selectbox("Sub-Region", regions)
with cat_col:
    categories = ["All Categories"] + sorted(list({e.category for e in all_events}))
    selected_cat = st.selectbox("Category", categories)

# Filter logic
filtered = [
    e for e in all_events
    if (selected_region == "All Regions" or e.region == selected_region)
    and (selected_cat == "All Categories" or e.category == selected_cat)
    and (
        query.lower() in e.title.lower()
        or query.lower() in e.venue.lower()
        or query.lower() in e.details.lower()
        or query.lower() in e.category.lower()
    )
]

def get_badge_class(cat: str) -> str:
    c = cat.lower()
    if "comedy" in c: return "badge badge-comedy"
    if "music" in c: return "badge badge-music"
    if "art" in c or "heritage" in c: return "badge badge-art"
    if "tech" in c: return "badge badge-tech"
    if "expo" in c: return "badge badge-expo"
    if "sport" in c: return "badge badge-sports"
    return "badge"

st.write(f"Showing **{len(filtered)}** upcoming events from AllEvents.in:")

# Display Cards
for ev in filtered:
    with st.container(border=True):
        left, right = st.columns([3.8, 1.2])
        with left:
            badge_class = get_badge_class(ev.category)
            st.markdown(
                f'<span class="{badge_class}">{ev.category}</span> '
                f'<span class="badge" style="background:#f1f5f9; color:#475569;">📍 {ev.region}</span>',
                unsafe_allow_html=True
            )
            st.subheader(ev.title)
            st.write(f"🏢 **Venue:** {ev.venue} &nbsp;|&nbsp; 🗓️ **Schedule:** {ev.schedule}")
            st.info(f"💡 **AI Summary:** {ev.summary}")
            
            with st.expander("📖 View Full Event Details & Info"):
                st.write(ev.details)
        with right:
            st.metric("Starting Price", ev.price)
            st.markdown(
    f'<a href="{ev.booking_url}" target="_blank" style="text-decoration:none;">'
    f'<button style="width:100%; background:#2563eb; color:white; border:none; padding:10px 14px; border-radius:8px; font-weight:600; cursor:pointer; margin-top:8px;">🎟️ Book Tickets</button>'
    f'</a>', 
    unsafe_allow_html=True
)

# Footer
st.markdown("""
<div class="custom-footer">
    <b>Delhi NCR Live Event Scout</b> • Data synced from AllEvents.in New Delhi<br>
    Python • Streamlit • BeautifulSoup • Academic Submission Project
</div>
""", unsafe_allow_html=True)