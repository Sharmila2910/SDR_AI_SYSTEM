from fastapi import APIRouter, Form, File, UploadFile, HTTPException
from pydantic import BaseModel
from utils import get_model
import io
import pdfplumber

router = APIRouter()

class EmailReviewRequest(BaseModel):
    """Model for the email review request data."""
    email_draft: str
    prospect_name: str
    company_name: str
    title: str
    snippet: str
    templates_file: UploadFile

@router.post("/review-email/")
async def review_email(
    email_draft: str = Form(...),
    prospect_name: str = Form(...),
    company_name: str = Form(...),
    title: str = Form(...),
    snippet: str = Form(...),
    templates_file: UploadFile = File(...),
):
    """Review and improve the email draft based on provided templates."""
    templates_content = ""

    #Template content from the uploaded file
    if templates_file.content_type == "application/pdf":
        with io.BytesIO(await templates_file.read()) as f:
            with pdfplumber.open(f) as pdf:
                for page in pdf.pages:
                    templates_content += page.extract_text()
    elif templates_file.content_type == "text/plain":
        templates_content = (await templates_file.read()).decode("utf-8")
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    try:
        model = get_model()

        #Feedback and Rating for the email draft
        feedback_prompt = f"""
        Review the following email draft and rate it out of 10 for each of the following factors:
        - Personalization
        - Clarity
        - Call-to-Action
        
        Email Draft:
        {email_draft}
        """
        feedback_response = model(feedback_prompt)
        feedback = feedback_response.strip()

        #Corrected email draft based on the template
        correction_prompt = f"""
        Help me to rewrite the email draft with including the prospect detail wherever it needs while using the best email templete for your reference, ensuring it is professional.
        Prospect Details:
        - Prospect Name: {prospect_name}
        - Company Name: {company_name}
        - Few Words about them: {snippet}
        Email Draft:
        {email_draft}
        
        Email Template:
        {templates_content}
        """
        corrected_response = model(correction_prompt)
        corrected_email = corrected_response.strip()

        return {
            "feedback": feedback,
            "corrected_email": corrected_email
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during email review: {e}")
