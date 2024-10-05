from fastapi import APIRouter, Form, File, UploadFile, HTTPException
from pydantic import BaseModel
from utils import get_model
import io
import pdfplumber

router = APIRouter()

class EmailGenerationRequest(BaseModel):
    """Model for the email generation request data."""
    prospect_name: str
    company_name: str
    title: str
    snippet: str

@router.post("/generate-email/")
async def generate_email(
    prospect_name: str = Form(...),
    company_name: str = Form(...),
    title: str = Form(...),
    snippet: str = Form(...),
    catalog_file: UploadFile = File(...)
):
    """Generate a personalized email draft based on the provided inputs and catalog."""
    catalog_content = ""

    #Content from the uploaded file
    if catalog_file.content_type == "application/pdf":
        with io.BytesIO(await catalog_file.read()) as f:
            with pdfplumber.open(f) as pdf:
                for page in pdf.pages:
                    catalog_content += page.extract_text()
    elif catalog_file.content_type == "text/plain":
        catalog_content = (await catalog_file.read()).decode("utf-8")
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type.")
    #Prompt for the model
    prompt = f"""
    You are an expert in crafting personalized sales emails. Write a professional email based on the following:
    1. Prospect Name: {prospect_name}
    2. Company Name: {company_name}
    3. Snippet: {snippet}
    Product Catalog:
    {catalog_content}
    Instructions:
    - After greeting, suggest one product from the catalog that would be most relevant to them (just name it, no explanation).
    - Include a call to action, like scheduling a demo.
    - End with a professional sign-off.
    - The email draft should not exceed 25 words and should not contain any emojis.
    - Provide only the email draft, without any additional content.
    Email Draft:
    """
    
    try:
        model = get_model()
        response = model(prompt)
        response_text = response if isinstance(response, str) else response.get('text', '')
        return {"email_draft": response_text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
