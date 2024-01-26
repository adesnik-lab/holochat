import importlib.metadata
from collections import defaultdict
from typing import Any
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .models import MessageContent, MessageHold, MessageRequest, MessageStore


app = FastAPI()

logo_path = Path(__file__).parent.parent / "logo"
app.mount("/logo", StaticFiles(directory=logo_path), name="logo")

templates_path = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=templates_path)

message_db: defaultdict[str, MessageStore] = defaultdict(MessageStore)


async def verify_db_key(dest_pc: str):
    """Verify that the target PC exists in the database."""
    if dest_pc not in message_db:
        raise HTTPException(status_code=404, detail="Client PC not found in message database.")


### --- Root --- ###

@app.get("/")
async def root(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        name="index.html", 
        request=request, 
        context={"version": f"v{importlib.metadata.version('holochat')}"}
    )

@app.get("/save/{dest_pc}")
async def save_db(dest_pc: str):
    out = message_db[dest_pc].model_dump_json(indent=2)
    fname = f"{dest_pc}_holochat_db.json"
    return StreamingResponse(out, media_type="application/json", 
                             headers={"Content-Disposition": "attachment; filename="+fname})

### --- Messages --- ###

# these routes must be defined first, before routes with the path parameter
@app.get("/msg/all", tags=["messages"])
async def read_all_messages():
    """Show all messages received by the server."""
    message_dict = {k: v.messages for k,v in message_db.items() if len(v.messages) > 0}
    return message_dict

@app.get("/msg/latest", tags=["messages"])
async def read_most_recent():
    """Show the most recent message for each client."""
    message_dict = {k: v.messages[-1] for k,v in message_db.items() if len(v.messages) > 0}
    return message_dict

@app.post("/msg/{dest_pc}", tags=["messages"])
async def write_message(dest_pc: str, msg: MessageContent):
    """Write a message to the database."""
    # take the raw message and turn it into a MessageHold (waiting for first GET request)
    new_msg = MessageHold(
        **msg.model_dump(), 
        target=dest_pc,
    )
    # message_db is a dict of lists, so we can append the new message to the list
    message_db[dest_pc].messages.append(new_msg)
    return {"message": "Message received.", "target": dest_pc}

@app.get("/msg/{dest_pc}", tags=["messages"], dependencies=[Depends(verify_db_key)])
async def read_message(dest_pc: str) -> MessageRequest:
    """Read a message from the database. This will return the most recent message for a client PC."""
    
    if len(message_db[dest_pc].messages) == 0:
        raise HTTPException(status_code=404, detail="No messages found for this client PC.")
    
    held_msg = message_db[dest_pc].messages[-1]
    
    if isinstance(held_msg, MessageRequest):
        held_msg.read_count += 1
    
    msg = MessageRequest(
        **held_msg.model_dump(exclude={"request_time"}),
    )
    message_db[dest_pc].messages[-1] = msg
    
    return msg

@app.delete("/msg/{dest_pc}", tags=["messages"], dependencies=[Depends(verify_db_key)])
async def delete_pc_messages(dest_pc: str) -> dict[str, str]:
    message_db[dest_pc].messages = []
    return {"message": "Messages deleted.", "target": dest_pc}

@app.delete("/msg", tags=["messages"])
async def delete_all_messages() -> dict[str, str]:
    for pc in message_db:
        message_db[pc].messages = []
    return {"message": "All messages deleted."}


### --- Config --- ###

@app.post("/config/{dest_pc}", tags=["config"])
async def write_config(dest_pc: str, config: dict[str, Any]):
    """Write a config to the database for a specific client."""
    message_db[dest_pc].config = config
    return {"message": "Config received.", "target": dest_pc}

@app.get("/config/{dest_pc}", tags=["config"], dependencies=[Depends(verify_db_key)])
async def read_config(dest_pc: str) -> dict[str, Any]:
    """Read a config from the database for a specific client."""
    if not message_db[dest_pc].config:
        raise HTTPException(status_code=404, detail="No config found for this client PC.")
    return message_db[dest_pc].config

@app.delete("/config/{dest_pc}", tags=["config"], dependencies=[Depends(verify_db_key)])
async def delete_pc_config(dest_pc: str) -> dict[str, str]:
    message_db[dest_pc].config.clear()
    return {"message": "Config deleted.", "target": dest_pc}

@app.get("/config", tags=["config"])
async def get_all_configs() -> dict[str, dict[str, Any]]:
    """Get all configs from the database."""
    return {k: v.config for k,v in message_db.items() if len(v.config) > 0}

@app.delete("/config", tags=["config"])
async def delete_all_configs() -> dict[str, str]:
    for pc in message_db:
        message_db[pc].config = {}
    return {"message": "All configs deleted."}


### --- Database --- ###

@app.get("/db", tags=["database"])
async def read_db_all() -> dict[str, MessageStore]:
    """Show the entire database."""
    return message_db

@app.get("/db/{dest_pc}", tags=["database"], dependencies=[Depends(verify_db_key)])
async def read_pc_db(dest_pc: str) -> MessageStore:
    """Show the database for a specific client."""
    return message_db[dest_pc]

@app.delete("/db/{dest_pc}", tags=["database"], dependencies=[Depends(verify_db_key)])
async def delete_pc_db(dest_pc: str) -> dict[str, str]:
    """Show the database for a specific client."""
    del message_db[dest_pc]
    return {"message": "Database deleted for target client.", "target": dest_pc}

@app.delete("/db", tags=["database"])
async def delete_db() -> dict[str, str]:
    message_db.clear()
    return {"message": "Database deleted."}