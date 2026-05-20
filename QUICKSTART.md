# Quick Start Guide (5 Minutes)

## TL;DR - Get Running Locally

### Step 1: Setup (2 mins)
```bash
cd meal_recommendation_system
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

### Step 2: MongoDB (2 mins)
1. Go to [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Sign up (free)
3. Create M0 cluster
4. Create database user
5. Whitelist your IP: 0.0.0.0 (testing only)
6. Copy connection string:
   ```
   mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
   ```
7. Edit `.env`:
   ```
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
   MONGODB_DB=meal_recommendation_db
   ```

### Step 3: Run (1 min)
```bash
streamlit run app.py
```
Browser opens to `http://localhost:8501`

## Test the App

### Signup
- Username: `testuser`
- Email: `test@example.com`
- Password: `password123`

### Complete Profile
- Fill in all fields
- Select disease (e.g., Diabetes)
- See real-time BMI/TDEE calculations

### Get Recommendations
- Go to Recommendations page
- View daily meal suggestions
- Generate 7-day meal plan

### View Analytics
- See 30-day charts
- Track calories & macros

## Deployment (3 mins)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Meal recommendation system"
   git push
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to share.streamlit.io
   - Click "New app"
   - Select your repo
   - Main file: `meal_recommendation_system/app.py`

3. **Add Secrets:**
   - Settings → Secrets
   - Add MONGODB_URI & MONGODB_DB

Done! App is live at: `https://username-repo.streamlit.app`

## File Structure

```
meal_recommendation_system/
├── app.py                    ← Main app
├── auth.py                   ← Login/signup
├── database.py               ← MongoDB
├── recommendation_engine.py  ← Core algorithm
├── pages/                    ← Dashboard, profile, etc.
├── nutrition_data.csv        ← Meal database
├── requirements.txt          ← Dependencies
└── README.md                 ← Full guide
```

## Key Features

✓ Signup/Login (bcrypt hashed)
✓ BMI & TDEE calculations
✓ Disease-specific meal recommendations
✓ 7-day meal planner
✓ 30-day analytics
✓ MongoDB integration

## Troubleshooting

**"Cannot connect to MongoDB"**
- Check MONGODB_URI in .env
- Verify IP whitelisted in MongoDB Atlas

**"ModuleNotFoundError"**
- Ensure virtual env activated
- Run: `pip install -r requirements.txt`

**"Streamlit won't start"**
- Check syntax: `python -m py_compile app.py`
- See DEPLOYMENT.md for more help

## Next Steps

1. Read README.md for features
2. Check RESUME_BULLETS.md for interview prep
3. Explore code in recommendation_engine.py
4. Deploy on Streamlit Cloud
5. Add to portfolio!

---

**Questions?** See README.md or DEPLOYMENT.md
