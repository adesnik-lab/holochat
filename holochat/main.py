from collections import defaultdict
from typing import Any

from fastapi import FastAPI, HTTPException, Request

from .models import MessageContent, MessageHold, MessageRequest, MessageStore


app = FastAPI()
message_db: defaultdict[str, MessageStore] = defaultdict(MessageStore)


### --- Root --- ###

@app.get("/")
async def root():
    return {"message": "Welcome to StimSync!"}


### --- Messages --- ###

# these routes must be defined first, before routes with the path parameter
@app.get("/msg/all")
async def read_all_messages():
    """Show all messages received by the server."""
    message_dict = {k: v.messages for k,v in message_db.items() if len(v.messages) > 0}
    return message_dict

@app.get("/msg/latest")
async def read_most_recent():
    """Show the most recent message for each client."""
    message_dict = {k: v.messages[-1] for k,v in message_db.items() if len(v.messages) > 0}
    return message_dict

@app.post("/msg/{dest_pc}")
async def write_message(dest_pc: str, msg: MessageContent,  request: Request):
    """Write a message to the database."""
    client_host = request.client.host #type: ignore
    # take the raw message and turn it into a MessageHold (waiting for first GET request)
    new_msg = MessageHold(
        **msg.model_dump(), 
        target=dest_pc,
        client_host=client_host, #type: ignore
    )
    # message_db is a dict of lists, so we can append the new message to the list
    message_db[dest_pc].messages.append(new_msg)
    return {"message": "Message received.", "target": dest_pc}

@app.get("/msg/{dest_pc}")
async def read_message(dest_pc: str) -> MessageRequest:
    """Read a message from the database. This will return the most recent message for a client PC."""
    
    if dest_pc not in message_db:
        raise HTTPException(status_code=404, detail="Client PC not found in message database.")
    
    if len(message_db[dest_pc].messages) == 0:
        raise HTTPException(status_code=404, detail="No messages found for this client PC.")
    
    held_msg = message_db[dest_pc].messages[-1]
    
    if isinstance(held_msg, MessageRequest):
        held_msg.read_count += 1
    
    msg = MessageRequest(
        **held_msg.model_dump(),
    )
    message_db[dest_pc].messages[-1] = msg
    
    return msg

@app.delete("/msg/{dest_pc}")
async def delete_pc_messages(dest_pc: str) -> dict[str, str]:
    if dest_pc not in message_db:
        raise HTTPException(status_code=404, detail="Client PC not found in message database.")
    else:
        message_db[dest_pc].messages = []
    return {"message": "Messages deleted.", "target": dest_pc}

@app.delete("/msg")
async def delete_all_messages() -> dict[str, str]:
    for pc in message_db:
        message_db[pc].messages = []
    return {"message": "All messages deleted."}


### --- Config --- ###

@app.post("/config/{dest_pc}")
async def write_config(dest_pc: str, config: dict[str, Any]):
    """Write a config to the database for a specific client."""
    message_db[dest_pc].config = config
    return {"message": "Config received.", "target": dest_pc}

@app.get("/config/{dest_pc}")
async def read_config(dest_pc: str) -> dict[str, Any]:
    """Read a config from the database for a specific client."""
    if dest_pc not in message_db:
        raise HTTPException(status_code=404, detail="Client PC not found in message database.")
    if not message_db[dest_pc].config:
        raise HTTPException(status_code=404, detail="No config found for this client PC.")
    return message_db[dest_pc].config

@app.delete("/config/{dest_pc}")
async def delete_pc_config(dest_pc: str) -> dict[str, str]:
    if dest_pc not in message_db:
        raise HTTPException(status_code=404, detail="Client PC not found in message database.")
    else:
        message_db[dest_pc].config.clear()
    return {"message": "Config deleted.", "target": dest_pc}

@app.get("/config")
async def get_all_configs() -> dict[str, dict[str, Any]]:
    """Get all configs from the database."""
    return {k: v.config for k,v in message_db.items() if len(v.config) > 0}

@app.delete("/config")
async def delete_all_configs() -> dict[str, str]:
    for pc in message_db:
        message_db[pc].config = {}
    return {"message": "All configs deleted."}


### --- Database --- ###

@app.get("/db")
async def read_db_all() -> dict[str, MessageStore]:
    """Show the entire database."""
    return message_db

@app.get("/db/{dest_pc}")
async def read_pc_db(dest_pc: str) -> MessageStore:
    """Show the database for a specific client."""
    if dest_pc not in message_db:
        raise HTTPException(status_code=404, detail="Client PC not found in message database.")
    return message_db[dest_pc]

@app.delete("/db/{dest_pc}")
async def delete_pc_db(dest_pc: str) -> dict[str, str]:
    """Show the database for a specific client."""
    if dest_pc not in message_db:
        raise HTTPException(status_code=404, detail="Client PC not found in message database.")
    del message_db[dest_pc]
    return {"message": "Database deleted for target client.", "target": dest_pc}

@app.delete("/db")
async def delete_db() -> dict[str, str]:
    message_db.clear()
    return {"message": "Database deleted."}