
import os
import json
import math
import re
from datetime import datetime, date, time, timedelta, timezone
from urllib.parse import quote_plus

import streamlit as st

try:
    from supabase import create_client
except ImportError:
    create_client = None

try:
    from google import genai
except ImportError:
    genai = None


# =========================================================
# CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="FoodRescue AI",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.block-container {
    max-width: 1440px;
    padding-top: 1.3rem;
    padding-bottom: 2.5rem;
}
.hero {
    padding: 1.6rem;
    border-radius: 18px;
    border: 1px solid rgba(75,160,110,.28);
    background: linear-gradient(120deg,
        rgba(35,140,85,.17), rgba(35,140,85,.035));
    margin-bottom: 1rem;
}
.eyebrow {
    color: #26945d;
    letter-spacing: .13em;
    font-size: .72rem;
    font-weight: 800;
    text-transform: uppercase;
}
div[data-testid="stMetric"] {
    border: 1px solid rgba(128,128,128,.22);
    padding: 14px;
    border-radius: 14px;
}
div.stButton > button,
div[data-testid="stFormSubmitButton"] button {
    border-radius: 10px;
    min-height: 2.5rem;
}
.muted { opacity: .72; font-size: .9rem; }
</style>
""", unsafe_allow_html=True)


def secret(*names):
    for name in names:
        try:
            value = st.secrets.get(name)
            if value:
                return str(value).strip()
        except Exception:
            pass
        value = os.getenv(name)
        if value:
            return value.strip()
    return ""


SUPABASE_URL = secret("SUPABASE_URL")
SUPABASE_KEY = secret("SUPABASE_ANON_KEY", "SUPABASE_PUBLISHABLE_KEY")
GEMINI_KEY = secret("GEMINI_API_KEY")
GOOGLE_MAPS_KEY = secret("GOOGLE_MAPS_API_KEY", "GOOGLE_MAPS_API")

sb = None
db_error = None

if create_client and SUPABASE_URL and SUPABASE_KEY:
    try:
        sb = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as exc:
        db_error = str(exc)
elif SUPABASE_URL and SUPABASE_KEY:
    db_error = "Install the supabase package."
else:
    db_error = "Supabase credentials are not configured."


# =========================================================
# SAMPLE DATA — SAFE DEFAULT FOR THE SUBMISSION DEMO
# Coordinates are illustrative demo locations in Varanasi.
# =========================================================

def seed_data():
    now = datetime.now(timezone.utc).isoformat()

    orgs = [
        {
            "id": "org1", "name": "Sunrise Community Kitchen",
            "org_type": "donor", "location": "Sigra, Varanasi",
            "latitude": 25.3176, "longitude": 82.9739,
            "capacity": 100, "food_preference": "any",
            "is_active": True,
        },
        {
            "id": "org2", "name": "Hope Food Foundation",
            "org_type": "ngo", "location": "Lanka, Varanasi",
            "latitude": 25.2677, "longitude": 83.0060,
            "capacity": 100, "food_preference": "vegetarian, prepared meals",
            "is_active": True,
        },
        {
            "id": "org3", "name": "Annapurna Care Centre",
            "org_type": "ngo", "location": "Bhelupur, Varanasi",
            "latitude": 25.2960, "longitude": 83.0005,
            "capacity": 45, "food_preference": "vegetarian, bakery",
            "is_active": True,
        },
        {
            "id": "org4", "name": "Green Leaf Canteen",
            "org_type": "donor", "location": "BHU, Varanasi",
            "latitude": 25.2670, "longitude": 82.9890,
            "capacity": 80, "food_preference": "any",
            "is_active": True,
        },
        {
            "id": "org5", "name": "City Relief Network",
            "org_type": "ngo", "location": "Chetganj, Varanasi",
            "latitude": 25.3220, "longitude": 82.9870,
            "capacity": 70, "food_preference": "any",
            "is_active": True,
        },
    ]

    volunteers_data = [
        {
            "id": "vol1", "full_name": "Aarav Sharma",
            "location": "Sigra, Varanasi", "latitude": 25.3120,
            "longitude": 82.9760, "availability": "available",
            "is_active": True,
        },
        {
            "id": "vol2", "full_name": "Priya Singh",
            "location": "Lanka, Varanasi", "latitude": 25.2700,
            "longitude": 83.0040, "availability": "available",
            "is_active": True,
        },
        {
            "id": "vol3", "full_name": "Rahul Verma",
            "location": "Bhelupur, Varanasi", "latitude": 25.2940,
            "longitude": 82.9990, "availability": "busy",
            "is_active": True,
        },
    ]

    donations_data = [
        {
            "id": "don1", "food_name": "Vegetarian meal boxes",
            "category": "Prepared meals", "quantity": 30,
            "description": "Freshly prepared vegetarian lunch boxes.",
            "location": "Sigra, Varanasi", "latitude": 25.3176,
            "longitude": 82.9739, "donor_org_id": "org1",
            "accepted_ngo_org_id": None, "status": "available",
            "pickup_deadline": (datetime.now(timezone.utc) +
                                timedelta(hours=3)).isoformat(),
            "storage_details": "Keep according to food handler guidance",
            "allergen_details": "Not verified; confirm with donor",
            "safety_confirmed": False, "created_at": now,
        },
        {
            "id": "don2", "food_name": "Fresh bananas and apples",
            "category": "Produce", "quantity": 45,
            "description": "Fresh fruit suitable for distribution.",
            "location": "BHU, Varanasi", "latitude": 25.2670,
            "longitude": 82.9890, "donor_org_id": "org4",
            "accepted_ngo_org_id": "org2", "status": "accepted",
            "pickup_deadline": (datetime.now(timezone.utc) +
                                timedelta(hours=5)).isoformat(),
            "storage_details": "Store appropriately",
            "allergen_details": "Confirm any cross-contact risks",
            "safety_confirmed": True, "created_at": now,
        },
        {
            "id": "don3", "food_name": "Bakery bread packs",
            "category": "Bakery", "quantity": 20,
            "description": "Sealed bread packs from a local bakery.",
            "location": "Chetganj, Varanasi", "latitude": 25.3220,
            "longitude": 82.9870, "donor_org_id": "org1",
            "accepted_ngo_org_id": "org5", "status": "collected",
            "pickup_deadline": (datetime.now(timezone.utc) +
                                timedelta(hours=2)).isoformat(),
            "storage_details": "Keep sealed",
            "allergen_details": "Check package labels",
            "safety_confirmed": True, "created_at": now,
        },
        {
            "id": "don4", "food_name": "Packaged snack boxes",
            "category": "Packaged food", "quantity": 25,
            "description": "Unopened snack boxes.",
            "location": "Bhelupur, Varanasi", "latitude": 25.2960,
            "longitude": 83.0005, "donor_org_id": "org4",
            "accepted_ngo_org_id": "org3", "status": "delivered",
            "pickup_deadline": (datetime.now(timezone.utc) +
                                timedelta(hours=1)).isoformat(),
            "storage_details": "Follow package instructions",
            "allergen_details": "Check package labels",
            "safety_confirmed": True, "created_at": now,
        },
    ]

    return orgs, donations_data, volunteers_data


if "demo_data" not in st.session_state:
    o, d, v = seed_data()
    st.session_state.demo_data = {
        "organizations": o,
        "donations": d,
        "volunteers": v,
    }

if "demo_counter" not in st.session_state:
    st.session_state.demo_counter = 100

if "ai_history" not in st.session_state:
    st.session_state.ai_history = []


# =========================================================
# DATA ACCESS
# =========================================================

def read_table(table):
    """Use Supabase when live mode is selected; otherwise use demo data."""
    if st.session_state.get("data_mode", "Demo data") == "Live Supabase":
        if not sb:
            return None, db_error
        try:
            rows = sb.table(table).select("*").limit(1000).execute().data
            return rows or [], None
        except Exception as exc:
            return None, str(exc)

    return st.session_state.demo_data[table], None


def insert_demo_donation(values):
    st.session_state.demo_counter += 1
    values["id"] = f"demo{st.session_state.demo_counter}"
    values["created_at"] = datetime.now(timezone.utc).isoformat()
    st.session_state.demo_data["donations"].insert(0, values)


def persist_insert(table, values):
    if st.session_state.get("data_mode") != "Live Supabase":
        if table == "donations":
            insert_demo_donation(values)
        else:
            st.session_state.demo_data[table].append(values)
        return True, None

    if not sb:
        return False, db_error

    try:
        response = sb.table(table).insert(values).execute()
        return bool(response.data), None
    except Exception as exc:
        return False, str(exc)


def persist_update(table, record_id, values):
    if st.session_state.get("data_mode") != "Live Supabase":
        rows = st.session_state.demo_data[table]
        for row in rows:
            if str(row.get("id")) == str(record_id):
                row.update(values)
                return True, None
        return False, "Record not found."

    if not sb:
        return False, db_error

    try:
        response = (
            sb.table(table).update(values).eq("id", record_id).execute()
        )
        if response.data:
            return True, None
        return False, "No row updated. Check table columns and Row Level Security."
    except Exception as exc:
        return False, str(exc)


def num(value):
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def norm(value):
    return str(value or "").strip().lower()


def kind(org):
    return norm(org.get("org_type") or org.get("organization_kind"))


def km(a, b):
    try:
        lat1, lon1 = float(a["latitude"]), float(a["longitude"])
        lat2, lon2 = float(b["latitude"]), float(b["longitude"])
        p1, p2 = math.radians(lat1), math.radians(lat2)
        dp = math.radians(lat2-lat1)
        dl = math.radians(lon2-lon1)
        h = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
        return 6371 * 2 * math.asin(min(1, math.sqrt(h)))
    except (KeyError, TypeError, ValueError):
        return None


def maps_url(origin, destination):
    return (
        "https://www.google.com/maps/dir/?api=1"
        f"&origin={quote_plus(str(origin))}"
        f"&destination={quote_plus(str(destination))}"
        "&travelmode=driving"
    )


# =========================================================
# AI: GEMINI EXTRACTION AND GROUNDED RAG
# =========================================================

def ask_gemini(prompt):
    if not GEMINI_KEY:
        return None, "Gemini API key is not configured."
    if genai is None:
        return None, "Install google-genai from requirements.txt."
    try:
        client = genai.Client(api_key=GEMINI_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        if not response.text:
            return None, "Gemini returned an empty response."
        return response.text.strip(), None
    except Exception as exc:
        return None, f"Gemini request failed: {exc}"


def extract_food(description):
    prompt = """
You extract food donation details. Return ONLY valid JSON with keys:
food_name, category, quantity, description, storage_details,
allergen_details, pickup_deadline.
Use null for unknown facts. Do not infer safety, expiry, allergens,
or a deadline not stated. Quantity should be numeric if stated.
Description:
""" + description[:3000]
    text, error = ask_gemini(prompt)
    if error:
        return None, error
    try:
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text,
                      flags=re.I).strip()
        data = json.loads(text)
        return data, None
    except Exception:
        return None, "Gemini did not return valid JSON. Try a shorter description."


def retrieve_context(question, donations, organizations):
    """Transparent keyword retrieval for this small demo knowledge base."""
    docs = []
    for d in donations:
        docs.append({
            "source": f"Donation {d.get('id')}",
            "text": (
                f"Food: {d.get('food_name')}; category: {d.get('category')}; "
                f"quantity: {d.get('quantity')}; status: {d.get('status')}; "
                f"location: {d.get('location')}; deadline: {d.get('pickup_deadline')}; "
                f"allergens: {d.get('allergen_details')}; "
                f"safety confirmed: {d.get('safety_confirmed')}"
            ),
        })
    for o in organizations:
        docs.append({
            "source": f"Organization {o.get('id')}",
            "text": (
                f"Name: {o.get('name')}; type: {kind(o)}; "
                f"location: {o.get('location')}; capacity: {o.get('capacity')}; "
                f"food preference: {o.get('food_preference')}; "
                f"active: {o.get('is_active')}"
            ),
        })

    words = set(re.findall(r"[a-z0-9]+", norm(question)))
    stop = {"which", "what", "where", "when", "does", "have", "with",
            "from", "that", "this", "can", "the", "for", "are", "and",
            "you", "our", "show", "tell", "about"}
    words -= stop

    ranked = []
    for doc in docs:
        content = norm(doc["text"])
        score = sum(1 for word in words if word in content)
        if score:
            ranked.append((score, doc))

    ranked.sort(key=lambda item: item[0], reverse=True)
    return [doc for _, doc in ranked[:6]]


# =========================================================
# SIDEBAR AND DATA MODE
# =========================================================

st.sidebar.markdown("## 🥗 FoodRescue AI")
st.sidebar.caption("Food recovery coordination")

data_mode = st.sidebar.radio(
    "Data source",
    ["Demo data", "Live Supabase"],
    index=0,
    help="Demo data is isolated from your real database.",
)
st.session_state.data_mode = data_mode

if data_mode == "Demo data":
    st.sidebar.success("Demo mode · No database writes")
else:
    if sb:
        st.sidebar.success("Supabase client initialized")
    else:
        st.sidebar.error("Supabase unavailable")
        st.sidebar.caption("Switch to Demo data to continue.")

role = st.sidebar.selectbox(
    "Preview workspace",
    ["Administrator", "Food donor", "NGO / recipient", "Volunteer"],
)
st.sidebar.caption("Prototype role switcher — not production authentication.")

if st.sidebar.button("Reset demo data", use_container_width=True):
    o, d, v = seed_data()
    st.session_state.demo_data = {
        "organizations": o, "donations": d, "volunteers": v
    }
    st.session_state.demo_counter = 100
    st.session_state.ai_history = []
    st.rerun()

st.sidebar.divider()
st.sidebar.markdown("**Integrations**")
st.sidebar.write("Gemini: " + ("Connected key configured" if GEMINI_KEY else "Optional key missing"))
st.sidebar.write("Google Maps: " + ("API key configured" if GOOGLE_MAPS_KEY else "Maps links available"))
st.sidebar.write("Supabase: " + ("Configured" if sb else "Not connected"))

orgs, org_error = read_table("organizations")
donations, don_error = read_table("donations")
volunteers, vol_error = read_table("volunteers")

load_errors = {
    "organizations": org_error,
    "donations": don_error,
    "volunteers": vol_error,
}
if any(load_errors.values()):
    st.warning("Some live tables could not be read. Check the connection and existing schema.")
    with st.expander("Connection diagnostics"):
        for table, error in load_errors.items():
            if error:
                st.write(f"**{table}:** {error}")

orgs = orgs or []
donations = donations or []
volunteers = volunteers or []
org_by_id = {str(o.get("id")): o for o in orgs}

pages = [
    "Overview", "Donations", "Create donation", "AI matching",
    "Live map", "Pickup tracking", "AI & RAG"
]
if role == "Food donor":
    pages = ["Overview", "Create donation", "Donations", "Live map", "Pickup tracking"]
elif role == "NGO / recipient":
    pages = ["Overview", "Donations", "AI matching", "Live map", "Pickup tracking"]
elif role == "Volunteer":
    pages = ["Overview", "Live map", "Pickup tracking"]

page = st.sidebar.radio("Workspace", pages)

st.markdown("""
<div class="hero">
  <div class="eyebrow">Food recovery · Intelligent coordination</div>
  <h1>🥗 FoodRescue AI</h1>
  <p>Connect surplus food with communities that need it.</p>
</div>
""", unsafe_allow_html=True)

if data_mode == "Demo data":
    st.info("DEMO MODE — all records and status changes are sample data.")
else:
    st.info("LIVE MODE — database data is subject to your Supabase permissions.")


# =========================================================
# OVERVIEW DASHBOARD
# =========================================================

if page == "Overview":
    available = [d for d in donations if norm(d.get("status")) == "available"]
    active_ngos = [o for o in orgs if o.get("is_active") is True and kind(o) in
                   ("ngo", "nonprofit", "charity")]
    active_donors = [o for o in orgs if o.get("is_active") is True and kind(o) in
                     ("donor", "canteen", "restaurant")]
    free_volunteers = [v for v in volunteers if v.get("is_active") is True and
                       norm(v.get("availability")) == "available"]

    st.subheader("Community impact")
    c = st.columns(4)
    c[0].metric("Available food listings", len(available))
    c[1].metric("Active NGOs", len(active_ngos))
    c[2].metric("Free volunteers", len(free_volunteers))
    c[3].metric("Active donors / canteens", len(active_donors))

    c = st.columns(4)
    c[0].metric("Available portions", int(sum(num(d.get("quantity")) for d in available)))
    c[1].metric("Accepted", sum(norm(d.get("status")) == "accepted" for d in donations))
    c[2].metric("Collected", sum(norm(d.get("status")) == "collected" for d in donations))
    c[3].metric("Delivered", sum(norm(d.get("status")) == "delivered" for d in donations))

    left, right = st.columns([1.3, 1])
    with left:
        st.subheader("Donation status")
        status_counts = {}
        for d in donations:
            status = str(d.get("status") or "unknown").title()
            status_counts[status] = status_counts.get(status, 0) + 1
        if status_counts:
            st.bar_chart(status_counts)
        else:
            st.info("No donation records available.")

    with right:
        st.subheader("Recent donations")
        for d in sorted(donations, key=lambda x: str(x.get("created_at", "")),
                        reverse=True)[:5]:
            with st.container(border=True):
                st.markdown(f"**{d.get('food_name', 'Food donation')}**")
                st.caption(f"{d.get('location', 'Location unknown')} · {d.get('quantity', 0)} portions")
                st.write(f"Status: **{str(d.get('status', 'unknown')).title()}**")

    st.caption("Meals rescued and environmental impact are not estimated unless a documented calculation is implemented.")


# =========================================================
# DONATION LIST
# =========================================================

elif page == "Donations":
    st.subheader("Food donations")
    search = st.text_input("Search by food, category or location")
    status_filter = st.selectbox("Status", ["All", "available", "accepted", "collected", "delivered"])
    filtered = donations[:]
    if status_filter != "All":
        filtered = [d for d in filtered if norm(d.get("status")) == status_filter]
    if search.strip():
        q = norm(search)
        filtered = [d for d in filtered if q in norm(" ".join(
            str(d.get(k, "")) for k in ("food_name", "category", "location", "description")
        ))]

    if not filtered:
        st.info("No matching donations.")
    for d in filtered:
        donor = org_by_id.get(str(d.get("donor_org_id")), {})
        with st.container(border=True):
            a, b = st.columns([3, 1])
            a.markdown(f"### {d.get('food_name', 'Food donation')}")
            a.write(f"{d.get('category', 'Uncategorised')} · {d.get('quantity', 0)} portions")
            a.caption(f"Donor: {donor.get('name', 'Unknown')} · {d.get('location', 'Location unknown')}")
            b.write(f"**{str(d.get('status', 'unknown')).title()}**")
            if not d.get("safety_confirmed"):
                st.warning("Food safety/allergen details need human verification.")
            st.caption(f"Allergens: {d.get('allergen_details') or 'Not specified'}")


# =========================================================
# CREATE DONATION + GEMINI
# =========================================================

elif page == "Create donation":
    st.subheader("Create a food listing")
    st.write("Describe the food naturally. Gemini can suggest structured fields for review.")

    with st.form("extract_form"):
        raw_description = st.text_area(
            "Food description",
            placeholder="Example: 30 vegetarian lunch boxes prepared today. Pickup before 7 PM.",
            height=110,
        )
        extract = st.form_submit_button("✨ Extract with Gemini", use_container_width=True)

    if extract:
        if not raw_description.strip():
            st.warning("Enter a description first.")
        else:
            extracted, error = extract_food(raw_description)
            if extracted:
                st.session_state.extracted = extracted
                st.session_state.raw_food_description = raw_description
                st.success("Extraction complete. Review the suggestions below.")
            else:
                st.error(error)

    extracted = st.session_state.get("extracted", {})
    categories = ["Prepared meals", "Produce", "Bakery", "Dairy", "Packaged food", "Other"]
    category_suggestion = norm(extracted.get("category"))
    default_category = next((x for x in categories if norm(x) == category_suggestion), categories[0])

    with st.form("create_donation"):
        food_name = st.text_input("Food name", value=str(extracted.get("food_name") or ""))
        category = st.selectbox("Category", categories, index=categories.index(default_category))
        quantity = st.number_input("Quantity / portions", min_value=1,
                                   value=max(1, int(num(extracted.get("quantity")) or 10)))
        description = st.text_area("Description", value=str(extracted.get("description") or st.session_state.get("raw_food_description", "")))
        location = st.text_input("Pickup location", value="Sigra, Varanasi")
        lat = st.number_input("Latitude", value=25.3176, format="%.6f")
        lon = st.number_input("Longitude", value=82.9739, format="%.6f")
        deadline_date = st.date_input("Pickup date", value=date.today(), min_value=date.today())
        deadline_time = st.time_input("Latest pickup time", value=time(18, 0))
        storage = st.text_input("Storage details", value=str(extracted.get("storage_details") or ""))
        allergens = st.text_input("Allergens", value=str(extracted.get("allergen_details") or "Not verified")
                                  )
        safety = st.checkbox("I have checked handling and allergen details.")
        submitted = st.form_submit_button("Publish donation", type="primary", use_container_width=True)

    if submitted:
        if not food_name.strip() or not location.strip():
            st.error("Food name and pickup location are required.")
        else:
            deadline = datetime.combine(deadline_date, deadline_time).replace(
                tzinfo=timezone.utc).isoformat()
            if data_mode == "Demo data":
                donor = next((o for o in orgs if kind(o) in ("donor", "canteen", "restaurant")), None)
                donor_id = donor["id"] if donor else "org1"
            else:
                donor = next((o for o in orgs if kind(o) in ("donor", "canteen", "restaurant")), None)
                donor_id = donor.get("id") if donor else None

            if not donor_id:
                st.error("No donor organization ID is available in live mode. Check your donor profile and schema.")
            else:
                values = {
                    "donor_org_id": donor_id,
                    "food_name": food_name.strip(),
                    "category": category,
                    "quantity": int(quantity),
                    "description": description.strip(),
                    "location": location.strip(),
                    "latitude": lat,
                    "longitude": lon,
                    "pickup_deadline": deadline,
                    "storage_details": storage,
                    "allergen_details": allergens,
                    "safety_confirmed": safety,
                    "status": "available",
                }
                ok, error = persist_insert("donations", values)
                if ok:
                    st.success("Donation published.")
                    st.session_state.extracted = {}
                    st.rerun()
                else:
                    st.error(f"Could not publish: {error}")


# =========================================================
# EXPLAINABLE RECIPIENT MATCHING
# =========================================================

elif page == "AI matching":
    st.subheader("Recipient matching")
    st.caption("Transparent rule-based ranking. Gemini can explain the results, but does not certify food safety.")

    available = [d for d in donations if norm(d.get("status")) == "available"]
    ngos = [o for o in orgs if o.get("is_active") is True and kind(o) in ("ngo", "nonprofit", "charity")]

    if not available or not ngos:
        st.info("Matching requires available donations and active NGO records.")
    else:
        selected = st.selectbox("Choose a donation", available,
                                format_func=lambda d: f"{d.get('food_name')} · {d.get('quantity')} portions")
        ranked = []
        for ngo in ngos:
            score, reasons = 0, []
            pref = norm(ngo.get("food_preference"))
            cat = norm(selected.get("category"))
            if not pref or pref in ("any", "all") or pref in cat or cat in pref:
                score += 3
                reasons.append("Recorded food preference is compatible or unrestricted.")
            else:
                reasons.append("Food preference needs manual review.")

            dist = km(selected, ngo)
            if dist is not None:
                if dist <= 5:
                    score += 3
                elif dist <= 20:
                    score += 2
                else:
                    score += 1
                reasons.append(f"Approximate straight-line distance: {dist:.1f} km.")
            else:
                reasons.append("Coordinates unavailable; distance was not scored.")

            capacity = num(ngo.get("capacity"))
            qty = num(selected.get("quantity"))
            if capacity >= qty:
                score += 2
                reasons.append("Recorded capacity covers the listed quantity.")
            else:
                reasons.append("Capacity may be insufficient; confirm with the NGO.")

            ranked.append((score, ngo, reasons, dist))
        ranked.sort(key=lambda x: x[0], reverse=True)

        for score, ngo, reasons, dist in ranked:
            with st.container(border=True):
                st.markdown(f"### {ngo.get('name')}")
                st.caption(f"{ngo.get('location')} · {dist:.1f} km straight-line distance" if dist is not None else ngo.get("location", ""))
                st.progress(min(100, int(score / 8 * 100)))
                st.caption(f"Explainable suitability score: {score}/8")
                for reason in reasons:
                    st.write("• " + reason)

                if st.button("Ask Gemini to explain this match", key=f"explain_{selected.get('id')}_{ngo.get('id')}"):
                    prompt = (
                        "Explain this food rescue recommendation clearly. Use only the provided facts; "
                        "mention uncertainty and do not claim food safety. Facts:\n"
                        + json.dumps({"donation": selected, "recipient": ngo, "reasons": reasons}, default=str)
                    )
                    answer, error = ask_gemini(prompt)
                    if answer:
                        st.info(answer)
                    else:
                        st.warning(error)

                if st.button("Accept donation", key=f"accept_{selected.get('id')}_{ngo.get('id')}",
                             disabled=(norm(selected.get("status")) != "available")):
                    ok, error = persist_update("donations", selected["id"], {
                        "status": "accepted",
                        "accepted_ngo_org_id": ngo["id"],
                    })
                    if ok:
                        st.success(f"Accepted by {ngo.get('name')}.")
                        st.rerun()
                    else:
                        st.error(f"Update failed: {error}")


# =========================================================
# GOOGLE MAPS / LOCATION VIEW
# =========================================================

elif page == "Live map":
    st.subheader("Food rescue map")
    st.caption("Demo coordinates are illustrative. Routes open in Google Maps; this is not live GPS tracking.")

    points = []
    for d in donations:
        try:
            points.append({
                "name": d.get("food_name", "Donation"),
                "type": "Donation",
                "latitude": float(d["latitude"]),
                "longitude": float(d["longitude"]),
                "status": d.get("status", "unknown"),
                "location": d.get("location", ""),
            })
        except (KeyError, TypeError, ValueError):
            pass

    for o in orgs:
        try:
            points.append({
                "name": o.get("name", "Organization"),
                "type": kind(o).upper(),
                "latitude": float(o["latitude"]),
                "longitude": float(o["longitude"]),
                "status": "active" if o.get("is_active") else "inactive",
                "location": o.get("location", ""),
            })
        except (KeyError, TypeError, ValueError):
            pass

    if points:
        st.map([{"latitude": p["latitude"], "longitude": p["longitude"]} for p in points],
               latitude="latitude", longitude="longitude", use_container_width=True)
        st.dataframe(points, use_container_width=True, hide_index=True)

        route_donations = [d for d in donations if norm(d.get("status")) in ("available", "accepted", "collected")]
        if route_donations:
            chosen = st.selectbox("Plan a sample route", route_donations,
                                  format_func=lambda d: f"{d.get('food_name')} — {d.get('location')}")
            recipients = [o for o in orgs if kind(o) in ("ngo", "nonprofit", "charity")]
            if recipients:
                recipient = st.selectbox("Destination NGO", recipients, format_func=lambda o: o.get("name", "NGO"))
                if st.button("Open route in Google Maps", type="primary"):
                    origin = f"{chosen.get('latitude')},{chosen.get('longitude')}"
                    destination = f"{recipient.get('latitude')},{recipient.get('longitude')}"
                    st.link_button("Open Google Maps directions", maps_url(origin, destination))
    else:
        st.info("No records with coordinates were found.")

    if GOOGLE_MAPS_KEY:
        st.caption("A Google Maps API key is configured. The pin map above uses Streamlit's map renderer; route links open Google Maps.")
    else:
        st.caption("For a Google Maps Platform embedded map, configure GOOGLE_MAPS_API_KEY and enable the applicable Google Maps API and billing.")


# =========================================================
# TRACKING
# =========================================================

elif page == "Pickup tracking":
    st.subheader("Pickup and delivery tracking")
    st.caption("The prototype simulates status transitions. A real deployment needs authorization policies for every transition.")

    if role == "Volunteer":
        st.info("Volunteer view: choose a delivery below and update its progress.")
    tracked = [d for d in donations if norm(d.get("status")) != "delivered"]

    if not tracked:
        st.success("No pending deliveries.")
    for d in tracked:
        with st.container(border=True):
            st.markdown(f"### {d.get('food_name', 'Donation')}")
            st.write(f"Quantity: {d.get('quantity', 0)} portions")
            st.write(f"Location: {d.get('location', 'Unknown')}")
            st.write(f"Current status: **{str(d.get('status')).title()}**")

            valid_next = {
                "available": ["accepted"],
                "accepted": ["collected"],
                "collected": ["delivered"],
            }
            status = norm(d.get("status"))
            next_states = valid_next.get(status, [])
            if next_states:
                next_status = next_states[0]
                if st.button(f"Demo: mark as {next_status}", key=f"status_{d.get('id')}"):
                    changes = {"status": next_status}
                    if next_status == "collected":
                        changes["collected_at"] = datetime.now(timezone.utc).isoformat()
                    if next_status == "delivered":
                        changes["delivered_at"] = datetime.now(timezone.utc).isoformat()
                    ok, error = persist_update("donations", d["id"], changes)
                    if ok:
                        st.success(f"Status changed to {next_status}.")
                        st.rerun()
                    else:
                        st.error(f"Status update failed: {error}")


# =========================================================
# RAG ASSISTANT
# =========================================================

elif page == "AI & RAG":
    st.subheader("FoodRescue AI assistant")
    st.caption("Retrieval-augmented generation: relevant records are retrieved first, then supplied to Gemini.")

    st.write("Try: **Which nearby NGO could accept 30 vegetarian prepared meals?**")
    question = st.text_area("Ask about donations, organizations or the workflow",
                            placeholder="Which organizations may accept available vegetarian food?")
    if st.button("Retrieve context and ask Gemini", type="primary", use_container_width=True):
        if not question.strip():
            st.warning("Enter a question.")
        else:
            evidence = retrieve_context(question, donations, orgs)
            if not evidence:
                st.warning("No relevant records were retrieved. Try mentioning a food type, location, NGO or quantity.")
            else:
                st.markdown("#### Retrieved evidence")
                for item in evidence:
                    with st.container(border=True):
                        st.caption(item["source"])
                        st.write(item["text"])

                prompt = (
                    "You are the FoodRescue AI assistant. Answer only from the supplied retrieved context. "
                    "Explain uncertainty. Do not invent records, availability, food safety, delivery completion, "
                    "or capacities. Recommend human verification for food safety. If evidence is insufficient, say so.\n\n"
                    f"Question: {question}\n\nRetrieved context:\n"
                    + "\n".join(f"[{x['source']}] {x['text']}" for x in evidence)
                )
                answer, error = ask_gemini(prompt)
                if answer:
                    st.markdown("#### Answer")
                    st.write(answer)
                    st.session_state.ai_history.append({
                        "question": question,
                        "answer": answer,
                        "sources": [x["source"] for x in evidence],
                    })
                else:
                    st.error(error)
                    st.info("The retrieved evidence above is still available; Gemini did not produce an answer.")

    if st.session_state.ai_history:
        with st.expander("Previous AI questions"):
            for item in reversed(st.session_state.ai_history[-5:]):
                st.markdown(f"**Q:** {item['question']}")
                st.write(item["answer"])
                st.caption("Sources: " + ", ".join(item["sources"]))


# =========================================================
# FOOTER
# =========================================================

st.divider()
st.caption(
    "FoodRescue AI · Prototype for food recovery coordination · "
    "SDG 2: Zero Hunger · SDG 12: Responsible Consumption and Production"
)
