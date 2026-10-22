# How to Launch and Host the ARQ Simulator Online (Public Access Guide)
**Student ID:** 25CS024 | **Course:** ITUC201 Fundamentals of Computer Networks

This guide explains how to host and deploy the ARQ Simulator (`app.py`) so that anyone in the world (professors, evaluators, classmates) can open and test it via a public link on any phone, tablet, or PC without installing anything.

---

## 🌟 Method 1: Streamlit Community Cloud (Recommended — Free, Permanent & Easiest)
*This is the gold-standard way to host Streamlit web apps. It gives you a permanent, secure HTTPS link like `https://arq-simulator-25cs024.streamlit.app` that runs 24/7 for free.*

### Step 1: Push Your Code to GitHub
1. Open your browser and go to [GitHub](https://github.com). Log in (or sign up).
2. Click **New Repository** (green button).
3. Name it: `arq-protocol-simulator` (set to **Public**).
4. In your terminal on your PC, run:
   ```bash
   cd "d:\Cse sem 3\Web devlopement\Practical 7_PHP form\ARQ_Project"
   git init
   git add .
   git commit -m "Initial commit of ARQ Simulator 25CS024"
   git branch -M main
   git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/arq-protocol-simulator.git
   git push -u origin main
   ```

### Step 2: Deploy on Streamlit Cloud (1-Click)
1. Go to [share.streamlit.io](https://share.streamlit.io).
2. Click **Continue with Google** (or Continue with GitHub).
3. Click **Create app** / **Deploy a new app**.
4. Fill in:
   - **Repository:** `<YOUR_GITHUB_USERNAME>/arq-protocol-simulator`
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL:** Customize to something clean like `arq-simulator-25cs024.streamlit.app`
5. Click **Deploy!**
6. Within 60 seconds, your application is live on the internet! You can paste this link into your submission proforma, presentation slides, and video description.

---

## 🚀 Method 2: Google Cloud Run (Official Google Cloud Platform Hosting)
*If you want the app hosted specifically on Google infrastructure (`*.run.app`). Google Cloud Run offers a generous free tier of 2 million requests per month.*

### Easy Way: Using Google Cloud Shell (No local software required!)
1. Open [Google Cloud Console](https://console.cloud.google.com/) with your Google Account.
2. In the top right corner, click the **Activate Cloud Shell** icon (`>_`).
3. Click the three dots `...` in Cloud Shell -> **Upload** -> upload your `ARQ_Project` zip or clone from GitHub.
4. Enter the directory and run:
   ```bash
   cd ARQ_Project
   gcloud run deploy arq-simulator \
     --source . \
     --region us-central1 \
     --allow-unauthenticated
   ```
5. Cloud Run will automatically build the container using the included `Dockerfile` and give you a public URL like:
   `https://arq-simulator-xxxxxx-uc.a.run.app`

---

## ⚡ Method 3: Instant 10-Second Public Link from Your PC (Localtunnel)
*If you need a live public URL right now to show someone during a call, viva, or video recording without uploading to GitHub.*

Your computer already has Node/npx installed!

1. **Terminal 1** (Start the simulator):
   ```powershell
   cd "d:\Cse sem 3\Web devlopement\Practical 7_PHP form\ARQ_Project"
   python -m streamlit run app.py
   ```
2. **Terminal 2** (Generate public link):
   ```powershell
   npx localtunnel --port 8501
   ```
3. Terminal 2 will output:
   ```text
   your url is: https://bright-tiger-12.loca.lt
   ```
4. Anyone on any mobile or desktop browser can open that URL to interact with your live simulator while your laptop is running.
*(Note: To verify the password on first open, your public IP is shown by visiting `https://loca.lt/mytunnelpassword`)*.

---

## 📓 Method 4: Google Colab (Run Directly on Google Servers)
1. Open [Google Colab](https://colab.research.google.com/).
2. Create a **New Notebook**.
3. In the first cell, paste and run:
   ```python
   # 1. Clone repository or download code
   !git clone https://github.com/<YOUR_GITHUB_USERNAME>/arq-protocol-simulator.git
   %cd arq-protocol-simulator
   
   # 2. Install requirements
   !pip install -r requirements.txt
   !npm install -g localtunnel
   
   # 3. Launch Streamlit in background and expose via localtunnel
   import urllib
   print("Password / Public IP is:", urllib.request.urlopen('https://ipv4.icanhazip.com').read().decode('utf8').strip())
   !streamlit run app.py & npx localtunnel --port 8501
   ```
4. Click the generated `loca.lt` link, enter the printed IP, and your simulator runs live on Google's cloud servers!
