from mcp.server.fastmcp import FastMCP
from tools import add_task, get_tasks, add_calendar_event, get_calendar_events, save_note, get_notes

mcp = FastMCP("CreatorOS")

@mcp.tool()
def create_task(title: str, due_date: str, category: str = "general") -> dict:
    """Add a new task to the CreatorOS workspace."""
    return add_task(title, due_date, category)

@mcp.tool()
def list_tasks(status: str = "pending") -> dict:
    """Retrieve tasks from the CreatorOS workspace."""
    return get_tasks(status)

@mcp.tool()
def schedule_event(event_title: str, event_date: str, event_time: str = "09:00") -> dict:
    """Schedule a calendar event in the CreatorOS workspace."""
    return add_calendar_event(event_title, event_date, event_time)

@mcp.tool()
def list_events(date: str = None) -> dict:
    """Retrieve calendar events from the CreatorOS workspace."""
    return get_calendar_events(date)

@mcp.tool()
def create_note(title: str, content: str, tag: str = "general") -> dict:
    """Save a note or idea to the CreatorOS workspace."""
    return save_note(title, content, tag)

@mcp.tool()
def list_notes(tag: str = None) -> dict:
    """Retrieve notes from the CreatorOS workspace."""
    return get_notes(tag)

if __name__ == "__main__":
    mcp.run(transport="stdio")
