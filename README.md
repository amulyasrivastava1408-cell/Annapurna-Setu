# 🍲 Annapurna Setu
### Annadaan Seva, Har Thali Tak.

**An AI-powered food rescue and redistribution platform connecting surplus food with communities that need it.**

Annapurna Setu aims to connect restaurants, canteens, NGOs, and volunteers to make food donation more organised, accessible, and efficient. By combining AI-assisted food processing, recipient matching, and location-aware coordination, the platform aims to reduce food waste and improve access to food.

---

## 🌱 The Problem

Every day, edible food can go to waste while communities continue to face food insecurity. Food donors and organisations serving people in need may struggle to coordinate food availability, quantities, collection times, and transportation.

Annapurna Setu aims to bridge this gap through a central platform for food donation and redistribution.

## 💡 Our Solution

Annapurna Setu provides a workflow for listing surplus food, discovering available donations, identifying suitable recipients, and coordinating pickups.

### Key Features

- 🍱 **Food Donation Management:** Create and view surplus food listings.
- 🤖 **AI-Assisted Food Details:** Use AI to extract structured information from food descriptions.
- 🎯 **Recipient Matching:** Identify potentially suitable recipients using factors such as food requirements, quantity, and location.
- 📍 **Location Support:** View locations and plan pickups using map integrations.
- 🚚 **Pickup Tracking:** Track donation progress through statuses such as available, accepted, collected, and delivered.
- 📊 **Impact Dashboard:** View donation activity, available portions, and redistribution progress.
- 💬 **AI Assistant — Future Development:** Build a chatbot that answers questions using current platform data through a Large Language Model (LLM) and Retrieval-Augmented Generation (RAG).

## 🛠️ Technology Stack

### Current Prototype

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Streamlit | Interactive web application |
| Supabase | Optional database integration |
| Google Gemini API | AI-assisted food information extraction and explanations |
| Streamlit Maps | Display location data in the prototype |
| Google Maps links | Help users open locations and plan routes |

The prototype supports demo data so users can explore its main workflows without requiring a live database connection.

### Planned Technology Evolution

As the project grows, the architecture may evolve towards:

- **Frontend:** React or Next.js for a responsive web application.
- **Mobile Application:** React Native or Flutter.
- **Backend:** FastAPI or Django with REST APIs.
- **Database:** AWS cloud.
- **AI and LLMs:** Gemini or another suitable LLM for food information extraction and conversational assistance.
- **RAG:** Retrieval from live donation, recipient, and platform records to provide context-aware answers.
- **Machine Learning:** Food categorisation and, when sufficient data is available, improved matching and demand prediction.
- **Maps and Location:** Google Maps Platform for geocoding, directions, and permission-based location features.
- **Notifications:** Email, SMS, or push notifications for donation acceptance and pickup updates.

These are planned improvements, not all currently implemented features.

## 🧠 How AI Fits In

The long-term vision is to use AI to improve the speed and quality of food redistribution.

1. **Information extraction:** Convert natural-language food descriptions into structured details.
2. **Intelligent matching:** Recommend recipients based on availability, quantity, urgency, distance, and suitability.
3. **Conversational assistance:** Use an LLM to answer user questions.
4. **RAG-based responses:** Retrieve relevant current platform records before generating answers.
5. **ML-based categorisation:** Train or evaluate models to categorise food and improve recommendations as reliable data becomes available.

AI recommendations will support human decision-making rather than replace food-safety checks or operational judgement.

## 🗺️ Location and Food Availability

The platform is intended to support location-aware food redistribution by helping donors and recipients coordinate collection.

The current prototype uses sample location data and map-based route links. Real-time food availability will require a connected, regularly updated database. Live location tracking will require appropriate user permissions and a location-sharing implementation.

## 👥 Who Can Use Annapurna Setu?

- **Food donors:** Restaurants, hotels, caterers, and canteens with surplus edible food.
- **Recipient organisations:** NGOs, community kitchens, shelters, and other eligible organisations.
- **Volunteers:** People who help collect and deliver donations.
- **Administrators:** People coordinating operations and monitoring platform activity.

## 🌍 Expected Impact

Annapurna Setu aims to contribute to:

- **SDG 2 — Zero Hunger:** Improve access to available food.
- **SDG 12 — Responsible Consumption and Production:** Reduce avoidable food waste.
- **SDG 13 — Climate Action:** Help prevent the environmental impact associated with wasted food.
- **SDG 17 — Partnerships for the Goals:** Strengthen coordination among donors, NGOs, and volunteers.

Potential impact measures include meals or portions redistributed, successful pickups, delivery completion rates, participating organisations, and estimated food waste prevented.

## 🚀 Development Roadmap

| Period | Planned focus |
|---|---|
| October | Improve the complete prototype, UI, AI workflows, reliability, and mobile responsiveness. |
| November | Conduct user outreach, gather feedback, and test workflows with potential donors, NGOs, and volunteers. |
| December | Refine usability, improve stability, prepare an initial launch, and evaluate user feedback. |

These are development goals and may change based on testing and available resources.

## ⚙️ Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/amulyasrivastava1408-cell/Annapurna-Setu.git
cd Annapurna-Setu
```

### 2. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure API credentials (optional for demo mode)

Create `.streamlit/secrets.toml` locally:

```toml
GEMINI_API_KEY = "your-gemini-api-key"
SUPABASE_URL = "your-supabase-project-url"
SUPABASE_ANON_KEY = "your-supabase-anon-key"
```

Only configure the services you need. Keep this file private and never commit API keys or other secrets to GitHub.

### 5. Run the application

```bash
python -m streamlit run app.py
```

Open the local URL displayed in your terminal, usually `http://localhost:8501`.

**Tip:** Start in demo mode to explore the prototype without depending on a live database.

## 🔐 Data and Security

- Demo mode uses sample data; changes in this mode are not persistent.
- Live database functionality depends on the configured Supabase schema, permissions, and application implementation.
- API credentials should be stored in environment variables or Streamlit secrets.
- A production release will require appropriate authentication, role-based access controls, data validation, privacy safeguards, and secure handling of location information.

## 🤝 Contributing

Ideas, feedback, and collaboration are welcome.

1. Fork the repository.
2. Create a branch for your changes.
3. Make and test your changes.
4. Submit a pull request describing the improvement.

## 🔮 Vision

Our vision is to build a scalable and accessible food redistribution network where technology helps surplus food reach the right people at the right time.

**Annapurna Setu — Annadaan Seva, Har Thali Tak.**

*Built with the belief that technology can help turn food surplus into community support.*

---

**Project:** Annapurna Setu  
**Focus:** AI for social impact, food rescue, sustainability, and community coordination  
**Repository:** https://github.com/amulyasrivastava1408-cell/Annapurna-Setu
