from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests

router = APIRouter()

#Google Custom Search API Keys
API_KEY = "AIzaSyBE_nUswAheraZXm9pI2xvWS8Q0q20vzvc"
SEARCH_ENGINE_ID = "27513c8150ab24c7a"
API_ENDPOINT = "https://www.googleapis.com/customsearch/v1"

class ResearchRequest(BaseModel):
    """Model for the research request data"""
    prospect_name: str
    company_name: str

@router.post("/research/")
async def research(data: ResearchRequest):
    """Fetch research data from Google Custom Search API."""
    query = f"{data.prospect_name} {data.company_name}"
    params = {
        "key": API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": query
    }

    try:
        response = requests.get(API_ENDPOINT, params=params)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"API request failed: {e}")

    search_results = response.json()
    items = search_results.get("items", [])
    
    if items:
        first_result = items[0]
        snippet = first_result.get("snippet", "No description available.")
        title = first_result.get("title", "No title available.")
        link = first_result.get("link", "No link available.")
    else:
        snippet = "No results found."
        title = "No results found."
        link = "No link found."

    return {
        "prospect_name": data.prospect_name,
        "company_name": data.company_name,
        "title": title,
        "link": link,
        "snippet": snippet
    }
