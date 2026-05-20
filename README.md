# 🥗 Patient-Specific Meal Recommendation System

A modern, production-ready healthcare application that generates personalized meal recommendations based on disease conditions, BMI, calorie requirements, dietary preferences, and health goals.

## ✨ Features

- **Personalized Recommendations**: AI-driven meal suggestions based on:
  - 5 medical conditions (Diabetes, Hypertension, Obesity, PCOS, Kidney Disease)
  - BMI and calorie targets
  - Dietary preferences (Vegetarian, Vegan, Gluten-Free, etc.)
  - Health goals (Weight Loss, Gain, Muscle Building, Maintenance)

- **Comprehensive Dashboard**: 
  - Real-time BMI & macro calculations
  - 7-day calorie tracking with charts
  - Personalized health metrics

- **User Profile Management**:
  - Secure authentication with password hashing
  - Detailed health profiling
  - BMR & TDEE calculations

- **Weekly Meal Planning**: Auto-generated 7-day meal plans

- **Nutrition Analytics**: 
  - 30-day macro trends
  - Meal type distribution
  - Logging history

- **Production-Grade Architecture**:
  - MongoDB Atlas integration
  - Modular code structure
  - Secure session management
  - Clean healthcare UI

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- MongoDB Atlas account (free tier available)
- Streamlit Cloud account (for deployment)

### Local Setup

1. **Clone and navigate to project:**
   ```bash
   cd meal_recommendation_system
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup MongoDB Atlas:**
   - Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
   - Create a free cluster
   - In Security → Network Access, add your IP (or 0.0.0.0 for testing)
   - Create a database user with credentials
   - Copy your connection string: `mongodb+srv://username:password@cluster.mongodb.net/`

5. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your MongoDB URI
   nano .env
   ```

6. **Run the app:**
   ```bash
   streamlit run app.py
   ```

   Open browser to `http://localhost:8501`

### MongoDB Collections Setup

Collections are created automatically on first run:

- **users**: User accounts (username, email, hashed password)
- **profiles**: User health data (age, weight, disease, goals)
- **meals**: Nutrition database (auto-seeded from CSV)
- **recommendation_history**: User meal logs

## 📊 Architecture

```
meal_recommendation_system/
├── app.py                          # Main Streamlit app entry
├── auth.py                         # Authentication & password hashing
├── database.py                     # MongoDB connection helpers
├── bmi_calculator.py               # BMI calculations
├── calorie_calculator.py           # TDEE & macro calculations
├── recommendation_engine.py        # Rule-based meal recommendation logic
├── utils.py                        # Shared UI components & styling
├── nutrition_data.csv              # 40+ sample meals with nutritional data
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variable template
├── pages/
│   ├── dashboard.py                # Main dashboard with KPIs
│   ├── profile.py                  # User profile management
│   ├── recommendations.py          # Meal recommendations & weekly planner
│   └── analytics.py                # Nutrition analytics & trends
└── README.md                       # This file
```

## 💡 Recommendation Engine Logic

### Disease-Specific Rules

**Diabetes**: 
- Max 5g sugar per meal
- Prefer: low-GI, high-fiber, low-sugar foods
- Avoid: refined carbs, sugary drinks

**Hypertension**:
- Max 400mg sodium per meal
- Prefer: low-sodium, potassium-rich, heart-healthy
- Avoid: processed, canned foods

**Obesity**:
- Single meal ≤ 30% daily calorie target
- Prefer: low-calorie, high-protein, high-fiber
- Avoid: fried, fast-food

**PCOS**:
- Max 8g sugar per meal
- Prefer: low-GI, anti-inflammatory
- Avoid: refined carbs, processed foods

**Kidney Disease**:
- Max 15g protein, 350mg sodium per meal
- Max potassium & phosphorus limits
- Prefer: kidney-friendly, low-protein
- Avoid: high-protein, high-mineral foods

### Scoring Algorithm

1. Filter meals violating hard restrictions
2. Score remaining meals by calorie/macro proximity
3. Bonus points for dietary preference matches
4. Return top N ranked by score

## 🔐 Security

- **Password Hashing**: bcrypt with salt
- **Session Management**: Streamlit session state
- **Input Validation**: Type checking and bounds
- **MongoDB Best Practices**: Parameterized queries

## 📈 Sample Data

CSV includes 40+ meals with tags:
- Breakfast, Lunch, Dinner, Snacks
- Vegetarian, Vegan, Gluten-Free, Dairy-Free
- Low-GI, High-Protein, Anti-Inflammatory, etc.

Auto-seeded into MongoDB on first load.

## 🌐 Deployment on Streamlit Cloud

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Initial meal recommendation system"
   git push
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your GitHub repo
   - Set main file path: `meal_recommendation_system/app.py`

3. **Add Secrets:**
   - In Streamlit Cloud app settings, add "Secrets":
     ```
     MONGODB_URI = "mongodb+srv://..."
     MONGODB_DB = "meal_recommendation_db"
     ```

## 📱 Usage

### Sign Up / Login
- Create account with email & password
- Login with credentials

### Complete Profile
- Enter height, weight, age, gender
- Select activity level, dietary preference, medical condition, goal

### View Dashboard
- See BMI, calorie targets, macro distribution
- 7-day calorie tracking chart

### Get Recommendations
- Browse daily meals by type
- View weekly auto-generated plan
- Check explanation for each meal

### Track Progress
- Log meals to history
- View 30-day analytics & trends

## 🎯 Resume Bullet Points

- Designed & developed full-stack healthcare MVP with 2000+ lines of production-grade Python
- Implemented rule-based recommendation engine supporting 5 disease conditions with nutrient-specific restrictions
- Built Streamlit UI with real-time BMI/macro calculations and interactive nutrition analytics
- Integrated MongoDB Atlas with 4 collections, auto-seeding from CSV; 40+ meal database with tags
- Engineered secure authentication using bcrypt hashing and session management
- Deployed multi-page app with modular architecture (8 core modules) following SOLID principles
- Created role-based meal scoring algorithm (calorie proximity + dietary tags + condition restrictions)
- Implemented 30-day nutrition trend analysis with Plotly charts and daily macro breakdown

## 🎓 Common Interview Questions & Answers

**Q: How does the recommendation engine handle conflicting restrictions?**
A: Hard constraints (e.g., max sodium) are applied first in a filter pass. If no meals pass, we log a warning and suggest loosening restrictions. Soft scoring (macro proximity) allows flexible trade-offs.

**Q: How would you scale this for 100k users?**
A: Add MongoDB indexing on (user_id, created_at) and (disease, tags). Cache recommendation results in Redis. Parallelize weekly plan generation with background workers. Implement pagination for history queries.

**Q: Why rule-based over ML?**
A: Medical constraints require hard guarantees (e.g., kidney patients MUST stay under protein limits). Rule-based allows transparent, auditable decisions critical for healthcare. ML can be added as a ranker on top.

**Q: How do you handle missing nutritional data?**
A: CSV has sensible defaults (0 for optional fields). In production, integrate USDA/FatSecret API. Validate data on insert; flag incomplete meals in admin panel.

**Q: How do you ensure data privacy?**
A: User passwords hashed with bcrypt; no plaintext storage. Recommend row-level security in MongoDB. In production, add encryption at rest, HTTPS, and GDPR compliance (data export/deletion endpoints).

**Q: What's the complexity of the scoring function?**
A: O(n) where n = filtered meals (~100-500). Per-meal scoring is O(1). Weekly plan generation: O(7 × 4) = O(1) constant iterations. Suitable for real-time response.

## 📝 Future Enhancements

- ML-based personalized ranker (collaborative filtering)
- Real USDA/FatSecret API integration
- Recipe variations & grocery list generation
- Wearable integration (Fitbit, Apple Health)
- Multi-language support
- Mobile app (React Native)
- Subscription tier & payment integration

## 📄 License

This project is provided as-is for educational and portfolio purposes.

---

**Built for BTech Internship/Placement Portfolio** | Production-Ready Healthcare MVP
