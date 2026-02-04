from fastapi import FastAPI, HTTPException, Response, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import boto3
import os
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME', 'events-table')
table = dynamodb.Table(table_name)

class Event(BaseModel):
    eventId: Optional[str] = None
    title: str
    descriptions: str
    date: str
    location: str
    capacity: int
    organizer: str
    status: str

@app.get("/")
def read_root():
    return {"message": "Event Management API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/events", status_code=201)
def create_event(event: Event):
    try:
        event_id = str(uuid.uuid4())
        item = {
            'eventId': event_id,
            'title': event.title,
            'descriptions': event.descriptions,
            'date': event.date,
            'location': event.location,
            'capacity': event.capacity,
            'organizer': event.organizer,
            'status': event.status
        }
        table.put_item(Item=item)
        return item
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events")
def list_events(status: Optional[str] = Query(None)):
    try:
        response = table.scan()
        items = response.get('Items', [])
        
        if status:
            items = [item for item in items if item.get('status') == status]
        
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events/{event_id}")
def get_event(event_id: str):
    try:
        response = table.get_item(Key={'eventId': event_id})
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail="Event not found")
        return response['Item']
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/events/{event_id}")
def update_event(event_id: str, event: Event):
    try:
        response = table.get_item(Key={'eventId': event_id})
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail="Event not found")
        
        item = {
            'eventId': event_id,
            'title': event.title,
            'descriptions': event.descriptions,
            'date': event.date,
            'location': event.location,
            'capacity': event.capacity,
            'organizer': event.organizer,
            'status': event.status
        }
        table.put_item(Item=item)
        return item
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/events/{event_id}")
def delete_event(event_id: str):
    try:
        response = table.get_item(Key={'eventId': event_id})
        if 'Item' not in response:
            raise HTTPException(status_code=404, detail="Event not found")
        
        table.delete_item(Key={'eventId': event_id})
        return {"message": "Event deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
