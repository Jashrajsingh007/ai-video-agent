import os
from datetime import datetime
from google.cloud import firestore
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

db = firestore.Client(project="zoo-agent-lab")

def add_task(title: str, due_date: str, category: str = "general") -> dict:
    """Adds a new task to the database."""
    doc_ref = db.collection("tasks").document()
    task = {"title": title, "due_date": due_date, "category": category, "status": "pending", "created_at": datetime.now().isoformat()}
    doc_ref.set(task)
    return {"status": "success", "message": f"Task '{title}' added due {due_date}"}

def get_tasks(status: str = "pending") -> dict:
    """Retrieves tasks from the database."""
    tasks = db.collection("tasks").where("status", "==", status).stream()
    result = [{"id": t.id, **t.to_dict()} for t in tasks]
    return {"tasks": result, "count": len(result)}

def add_calendar_event(event_title: str, event_date: str, event_time: str = "09:00") -> dict:
    """Adds an event to the calendar."""
    doc_ref = db.collection("calendar").document()
    event = {"title": event_title, "date": event_date, "time": event_time, "created_at": datetime.now().isoformat()}
    doc_ref.set(event)
    return {"status": "success", "message": f"Event '{event_title}' scheduled on {event_date} at {event_time}"}

def get_calendar_events(date: str = None) -> dict:
    """Retrieves calendar events."""
    ref = db.collection("calendar")
    events = ref.where("date", "==", date).stream() if date else ref.stream()
    result = [{"id": e.id, **e.to_dict()} for e in events]
    return {"events": result, "count": len(result)}

def save_note(title: str, content: str, tag: str = "general") -> dict:
    """Saves a note or idea to the database."""
    doc_ref = db.collection("notes").document()
    note = {"title": title, "content": content, "tag": tag, "created_at": datetime.now().isoformat()}
    doc_ref.set(note)
    return {"status": "success", "message": f"Note '{title}' saved successfully"}

def get_notes(tag: str = None) -> dict:
    """Retrieves notes from the database."""
    ref = db.collection("notes")
    notes = ref.where("tag", "==", tag).stream() if tag else ref.stream()
    result = [{"id": n.id, **n.to_dict()} for n in notes]
    return {"notes": result, "count": len(result)}

def research_topic(topic: str) -> dict:
    """Researches a topic using Wikipedia."""
    wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(top_k_results=2, doc_content_chars_max=1000))
    result = wiki.run(topic)
    return {"topic": topic, "summary": result}