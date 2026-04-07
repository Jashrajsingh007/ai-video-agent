\# 🎬 CreatorOS — Multi-Agent AI Video Production Suite



An AI-powered video production assistant built with Google Gemini,

MCP (Model Context Protocol), and Cloud Run.



\## ✨ Features

\- Multi-agent pipeline for AI video production

\- Google Gemini powered intelligence

\- MCP server for tool orchestration

\- Deployed on Google Cloud Run



\## 🚀 Setup



\### 1. Clone the repo

git clone https://github.com/Jashrajsingh007/ai-video-agent.git

cd ai-video-agent



\### 2. Install dependencies

pip install -r requirements.txt



\### 3. Add your credentials

Copy .env.example → .env and fill in your keys:

\- GOOGLE\_API\_KEY → from aistudio.google.com

\- GOOGLE\_APPLICATION\_CREDENTIALS → path to your serviceaccount.json

&#x20; (download from Google Cloud Console → IAM → Service Accounts)



\### 4. Run

python app.py



\## 🛠️ Tech Stack

\- Python + FastAPI

\- Google Gemini API

\- MCP (Model Context Protocol)

\- Google Cloud Run

\- Firebase / Firestore



\## ⚠️ Note

Never commit .env or serviceaccount.json — see .env.example for

required environment variables.



\## 👤 Author

Jashraj Singh

