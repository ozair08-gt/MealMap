# Deployment Guide

## Local Development

### Quick Start
```bash
cd meal_recommendation_system
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your MongoDB URI
streamlit run app.py
```

Visit `http://localhost:8501`

## MongoDB Atlas Setup (5 mins)

1. **Create Account**
   - Go to [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
   - Sign up (free tier available)

2. **Create Cluster**
   - Click "Build a Deployment"
   - Select "M0" (free tier)
   - Choose region (closest to you)
   - Create cluster (takes ~3 minutes)

3. **Network Access**
   - Go to Security → Network Access
   - Click "Add IP Address"
   - For testing: Add "0.0.0.0/0" (allow all)
   - For production: Add your server IP only

4. **Database User**
   - Go to Security → Database Access
   - Click "Add New Database User"
   - Set username & password
   - Save credentials securely

5. **Get Connection String**
   - Go to Deployment → Databases
   - Click "Connect"
   - Select "Drivers"
   - Copy connection string:
     ```
     mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
     ```
   - Replace `username`, `password`, and `cluster` name

6. **Test Connection**
   ```bash
   python -c "from meal_recommendation_system.database import check_connection; print(check_connection())"
   ```

## Streamlit Cloud Deployment

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Patient meal recommendation system"
git remote add origin https://github.com/your-username/repo-name.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Authenticate with GitHub
4. Select repository
5. Set main file: `meal_recommendation_system/app.py`
6. Click "Deploy"

### Step 3: Add Secrets
1. In app settings (gear icon) → Secrets
2. Add:
   ```
   MONGODB_URI = "mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority"
   MONGODB_DB = "meal_recommendation_db"
   ```
3. Save & redeploy

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB Atlas connection | `mongodb+srv://...` |
| `MONGODB_DB` | Database name | `meal_recommendation_db` |

## Production Checklist

- [ ] MongoDB cluster in production tier (M2+)
- [ ] Network restricted to app server IP only
- [ ] Database backups enabled
- [ ] SSL certificate for custom domain
- [ ] Rate limiting enabled
- [ ] Password requirements enforced
- [ ] Secrets in environment, never .env
- [ ] Error logging configured
- [ ] Monitoring alerts set up

## Troubleshooting

**"Cannot connect to MongoDB"**
- Check MONGODB_URI in .env
- Verify IP is whitelisted in Network Access
- Ensure database user has correct password

**"ModuleNotFoundError"**
- Verify requirements.txt installed: `pip install -r requirements.txt`
- Check virtual environment is activated

**"Streamlit app not starting"**
- Run: `streamlit run app.py --logger.level=debug`
- Check for syntax errors: `python -m py_compile app.py`

**Slow recommendations**
- Add index: `db.meals.createIndex({"tags": 1})`
- Cache results with @st.cache_resource

## Performance Tips

1. **Database Indexing**
   ```javascript
   db.meals.createIndex({ "tags": 1 })
   db.recommendation_history.createIndex({ "user_id": 1, "created_at": -1 })
   db.profiles.createIndex({ "user_id": 1 })
   ```

2. **Caching**
   ```python
   @st.cache_resource
   def load_meals():
       return list(get_meals_collection().find())
   ```

3. **Query Limits**
   - Use pagination for large result sets
   - Add .limit(1000) to history queries

## Monitoring

Check Streamlit Cloud logs:
- View in app settings → Logs
- Filter by error level
- Set alerts for failures

Monitor MongoDB:
- Atlas Dashboard → Charts
- Check connection count, CPU, memory
- Review slow queries

## Custom Domain

1. Buy domain (Namecheap, GoDaddy, etc.)
2. In Streamlit Cloud settings → Custom domain
3. Add CNAME record pointing to Streamlit servers
4. Wait for DNS propagation (~24 hours)

## Scaling

- **0-1k users**: M0 MongoDB + Streamlit free tier
- **1k-10k users**: M2 MongoDB + Streamlit $5/month
- **10k+ users**: M5+ MongoDB + custom Streamlit deployment

---

For issues, check MongoDB docs or Streamlit forums.
