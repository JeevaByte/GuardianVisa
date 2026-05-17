# MongoDB Atlas Setup Guide — GuardianVisa

## Section 1: Create Free Cluster

1. Go to https://cloud.mongodb.com → Sign up / Log in
2. Click **"Create"** → Choose **"M0 Free"** tier
3. Provider: **AWS**, Region: **us-east-1** (or nearest)
4. Cluster name: `guardianvisa-cluster`
5. Click **"Create Deployment"**

---

## Section 2: Create Database User

1. **Security** → **Database Access** → **Add New Database User**
2. Username: `guardianvisa-user`
3. Password: generate a strong password *(copy it — you won't see it again!)*
4. Role: **"Read and write to any database"**
5. Click **"Add User"**

---

## Section 3: Network Access (Allow All for Demo)

1. **Security** → **Network Access** → **Add IP Address**
2. Click **"Allow Access from Anywhere"** (`0.0.0.0/0`)
3. > ⚠️ **Note:** For production, restrict to your Cloud Run IP only.
4. Click **"Confirm"**

---

## Section 4: Get Connection String

1. **Overview** → **Connect** → **"Drivers"**
2. Driver: **Python**, Version: **3.12+**
3. Copy the connection string — it looks like:
   ```
   mongodb+srv://guardianvisa-user:<password>@guardianvisa-cluster.xxxxx.mongodb.net/
   ```
4. Replace `<password>` with your actual password
5. Append the database name — add `guardianvisa` after the last `/`

   **Full URI:**
   ```
   mongodb+srv://guardianvisa-user:PASSWORD@guardianvisa-cluster.xxxxx.mongodb.net/guardianvisa
   ```

---

## Section 5: Set Environment Variable

```bash
# In backend/.env
MONGODB_URI=mongodb+srv://guardianvisa-user:PASSWORD@guardianvisa-cluster.xxxxx.mongodb.net/guardianvisa
```

---

## Section 6: Seed the Database

```bash
cd /path/to/GuardianVisa
pip install pymongo python-dotenv
python data/seed_mongodb.py
```

**Expected output:**
```
✅ Seeded 3 docs into 'students'
✅ Seeded 4 docs into 'visa_rules'
✅ Seeded 8 docs into 'scam_patterns'
✅ Seeded 18 docs into 'emergency_resources'
🎉 All collections seeded successfully!
```

---

## Section 7: Verify in Atlas UI

1. **Browse Collections** → `guardianvisa` database
2. Confirm all 4 collections exist with correct document counts:

   | Collection           | Expected Docs |
   |----------------------|---------------|
   | `students`           | 3             |
   | `visa_rules`         | 4             |
   | `scam_patterns`      | 8             |
   | `emergency_resources`| 18            |

3. Take a screenshot for demo evidence.

---

## MongoDB MCP Server Setup (Required for Hackathon)

```bash
# Install MongoDB MCP server
npm install -g @mongodb-js/mongodb-mcp-server

# Run MCP server (in a separate terminal)
MONGODB_URI="your-uri" mongodb-mcp-server

# Default port: 3001
```

---

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `MongoServerSelectionTimeoutError` | IP not whitelisted | Go to **Security → Network Access** and ensure `0.0.0.0/0` is added |
| `Authentication failed` | Wrong username or password in URI | Double-check `MONGODB_URI` — username and password must match what was set in **Database Access** |
| `database not found` | Database name missing from URI | Ensure the URI ends with `/guardianvisa`, e.g. `...mongodb.net/guardianvisa` |
