import os
import vertexai
from vertexai.generative_models import GenerativeModel
import firebase_admin
from firebase_admin import credentials, firestore as fb_firestore
from datetime import datetime
from dotenv import load_dotenv
from tools import add_task, get_tasks, add_calendar_event, get_calendar_events, save_note, get_notes, research_topic

load_dotenv()

# Initialize Vertex AI
vertexai.init(project="zoo-agent-lab", location="europe-west1")
model = GenerativeModel("gemini-2.5-flash")

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceaccount.json")
    firebase_admin.initialize_app(cred)
db = fb_firestore.client()

# ── AGENT 1: COMPOSITION ──
def pick_composition(prompt: str) -> str:
    response = model.generate_content(f"""
You are a video composition expert. Based on this topic: "{prompt}"
Choose the BEST composition from:
- SaasVideo: for tech products, startups, software, business tools
- MotivationalVideo: for inspiration, fitness, success, mindset
- LuxuryShorts60sPremium: for luxury brands, premium products, lifestyle
- AluxScene: for storytelling, education, general topics
Reply with ONLY the composition name, nothing else.
""")
    return response.text.strip()

# ── AGENT 2: STRATEGY ──
def generate_strategy(prompt: str, composition: str) -> str:
    response = model.generate_content(f"""
You are a world-class content strategist for {composition} style videos.
Topic: "{prompt}"
Provide:
1. TARGET AUDIENCE
2. KEY MESSAGE
3. EMOTIONAL HOOK
4. CALL TO ACTION
5. VISUAL TONE
Be concise and specific.
""")
    return response.text

# ── AGENT 3: SCRIPT ──
def generate_script(prompt: str, composition: str, strategy: str) -> str:
    style_guides = {
        "SaasVideo": "Clean, minimal, professional. Focus on features and benefits. Strong CTA.",
        "MotivationalVideo": "Bold, punchy, emotional. Power words. Short sentences.",
        "LuxuryShorts60sPremium": "Sophisticated, aspirational. Slow pace. Lifestyle focus.",
        "AluxScene": "Storytelling, cinematic, narrative-driven."
    }
    style = style_guides.get(composition, "Professional and engaging")
    response = model.generate_content(f"""
You are an expert scriptwriter for {composition} Remotion animations.
STYLE: {style}
STRATEGY: {strategy}
TOPIC: {prompt}
Write a 30-second script:
- TITLE
- SCENE 1 (0-8s): Visual + Narration (max 15 words)
- SCENE 2 (8-20s): Visual + Narration (max 15 words)
- SCENE 3 (20-30s): Visual + Narration + CTA (max 15 words)
""")
    return response.text

# ── AGENT 4: REMOTION PROMPT ──
def generate_remotion_prompt(prompt: str, composition: str, script: str, strategy: str) -> str:
    response = model.generate_content(f"""
You are an expert Remotion developer. Generate an EXTREMELY DETAILED coding prompt
for any AI coder to create a perfect Remotion video.
COMPOSITION: {composition}
TOPIC: {prompt}
SCRIPT: {script}
STRATEGY: {strategy}
Include:
1. Exact text for each scene
2. Animation specs with frame timing at 30fps
3. Color palette (hex codes)
4. Typography details
5. Layout and positioning
6. Transitions between scenes
7. Background style
Make it so detailed zero creative decisions are left to the coder.
""")
    return response.text

# ── AGENT 5: TASK MANAGER ──
def run_task_agent(prompt: str) -> dict:
    response = model.generate_content(f"""
Extract task details from this request: "{prompt}"
Return in this exact format:
TITLE: [task title]
DUE_DATE: [YYYY-MM-DD format, use today if not specified: {datetime.now().strftime('%Y-%m-%d')}]
CATEGORY: [video/research/social/general]
""")
    lines = response.text.strip().split('\n')
    title = due_date = category = ""
    for line in lines:
        if line.startswith("TITLE:"): title = line.replace("TITLE:", "").strip()
        elif line.startswith("DUE_DATE:"): due_date = line.replace("DUE_DATE:", "").strip()
        elif line.startswith("CATEGORY:"): category = line.replace("CATEGORY:", "").strip()
    if title:
        return add_task(title, due_date, category)
    return {"status": "skipped"}

# ── AGENT 6: CALENDAR ──
def run_calendar_agent(prompt: str, composition: str) -> dict:
    response = model.generate_content(f"""
Create a calendar event for this video project: "{prompt}"
Composition type: {composition}
Return in this exact format:
TITLE: [event title]
DATE: [YYYY-MM-DD, use next week: {datetime.now().strftime('%Y-%m-%d')}]
TIME: [HH:MM, default 10:00]
""")
    lines = response.text.strip().split('\n')
    title = date = time = ""
    for line in lines:
        if line.startswith("TITLE:"): title = line.replace("TITLE:", "").strip()
        elif line.startswith("DATE:"): date = line.replace("DATE:", "").strip()
        elif line.startswith("TIME:"): time = line.replace("TIME:", "").strip()
    if title:
        return add_calendar_event(title, date, time)
    return {"status": "skipped"}

# ── SAVE TO FIRESTORE ──
def save_to_firestore(data: dict) -> str:
    doc_ref = db.collection("video_requests").add({
        **data,
        "timestamp": datetime.now().isoformat(),
        "status": "ready_to_render"
    })
    return doc_ref[1].id

# ── MAIN COORDINATOR ──
def run_agent(user_prompt: str) -> dict:
    print(f"\n🎬 CreatorOS Processing: {user_prompt}")

    print("🎨 Composition Agent...")
    composition = pick_composition(user_prompt)
    print(f"✅ Selected: {composition}")

    print("🧠 Strategy Agent...")
    strategy = generate_strategy(user_prompt, composition)

    print("📝 Script Agent...")
    script = generate_script(user_prompt, composition, strategy)

    print("💻 Remotion Prompt Agent...")
    remotion_prompt = generate_remotion_prompt(user_prompt, composition, script, strategy)

    print("✅ Task Agent saving task...")
    task_result = run_task_agent(user_prompt)

    print("📅 Calendar Agent scheduling...")
    calendar_result = run_calendar_agent(user_prompt, composition)

    result = {
        "prompt": user_prompt,
        "composition": composition,
        "strategy": strategy,
        "script": script,
        "remotion_coding_prompt": remotion_prompt,
        "render_command": f"npx remotion render {composition} output.mp4",
        "task": task_result,
        "calendar": calendar_result
    }

    print("💾 Saving to Firestore...")
    doc_id = save_to_firestore(result)
    result["doc_id"] = doc_id

    return result

if __name__ == "__main__":
    result = run_agent("Create a product launch video for my AI SaaS tool called TaskFlow")
    print("\n✅ RESULT:")
    print(f"Composition: {result['composition']}")
    print(f"Task: {result['task']}")
    print(f"Calendar: {result['calendar']}")