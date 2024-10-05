import streamlit as st
import requests

#FastAPI
FASTAPI_URL = "http://127.0.0.1:8080"

def main():
    st.title("SDR AI System")

    #Session state variables
    if "research_data" not in st.session_state:
        st.session_state.research_data = None
    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None
    if "email_draft" not in st.session_state:
        st.session_state.email_draft = ""
    if "reviewed_email" not in st.session_state:
        st.session_state.reviewed_email = ""
    if "feedback" not in st.session_state:
        st.session_state.feedback = ""
    if "prospect_email" not in st.session_state:
        st.session_state.prospect_email = ""
    if "monitoring_status" not in st.session_state:
        st.session_state.monitoring_status = ""

    # Prospect Research Form
    st.header("Researching the Prospect")
    prospect_name = st.text_input("Prospect Name")
    company_name = st.text_input("Company Name")
    prospect_email = st.text_input("Prospect Email")

    if st.button("Fetch Data About them"):
        if prospect_name and company_name and prospect_email:
            response = requests.post(f"{FASTAPI_URL}/research/", json={
                "prospect_name": prospect_name,
                "company_name": company_name
            })
            if response.status_code == 200:
                st.session_state.research_data = response.json()
                st.session_state.prospect_email = prospect_email
            else:
                st.error("Failed to fetch data.")
        else:
            st.error("Please enter all required fields.")

    #Research Report
    if st.session_state.research_data:
        research_data = st.session_state.research_data
        st.write("Research Report:")
        st.write(f"Prospect Name: {research_data['prospect_name']}")
        st.write(f"Company Name: {research_data['company_name']}")
        st.write(f"Title: {research_data['title']}")
        st.write(f"Link: {research_data['link']}")
        st.write(f"Snippet: {research_data['snippet']}")

        # Upload Catalog file
        st.header("Email Generation")
        st.session_state.uploaded_file = st.file_uploader("Upload Product Catalog", type=["txt", "pdf"])

        if st.button("Generate Email"):
            if st.session_state.uploaded_file:
                uploaded_file = st.session_state.uploaded_file
                file_content = uploaded_file.read()

                email_request_data = {
                    "prospect_name": st.session_state.research_data['prospect_name'],
                    "company_name": st.session_state.research_data['company_name'],
                    "title": st.session_state.research_data['title'],
                    "snippet": st.session_state.research_data['snippet']
                }

                files = {
                    "catalog_file": (uploaded_file.name, file_content, uploaded_file.type)
                }

                email_response = requests.post(f"{FASTAPI_URL}/generate-email/", data=email_request_data, files=files)

                if email_response.status_code == 200:
                    st.session_state.email_draft = email_response.json().get("email_draft")
                    st.text_area("Generated Email Draft", value=st.session_state.email_draft, height=300)
                else:
                    st.error(f"Failed to generate email. Status Code: {email_response.status_code}. Response: {email_response.text}")
            else:
                st.error("Please upload the product catalog.")
       
        
        # Email Review
        if st.session_state.email_draft:
            st.header("Email Review")
            st.text_area("Email Draft Generated", value=st.session_state.email_draft, height=300)

            # Upload Email template
            templates_file = st.file_uploader("Upload Sales Email Template", type=["txt", "pdf"])

            if st.button("Review Email"):
                if templates_file:
                    templates_content = templates_file.read()

                    files = {
                        "templates_file": (templates_file.name, templates_content, templates_file.type)
                    }

                    review_request_data = {
                        "email_draft": st.session_state.email_draft,
                        "prospect_name": st.session_state.research_data['prospect_name'],
                        "company_name": st.session_state.research_data['company_name'],
                        "title": st.session_state.research_data['title'],
                        "snippet": st.session_state.research_data['snippet']
                    }

                    review_response = requests.post(f"{FASTAPI_URL}/review-email/", data=review_request_data, files=files)

                    if review_response.status_code == 200:
                        try:
                            response_json = review_response.json()
                            if response_json:
                                st.session_state.feedback = response_json.get("feedback", "No feedback available.")
                                st.session_state.reviewed_email = response_json.get("corrected_email", "No corrected email available.")
                                
                                st.text_area("Feedback and Rating", value=st.session_state.feedback, height=300)
                                st.text_area("Corrected Email Draft", value=st.session_state.reviewed_email, height=300)
                            else:
                                st.error("The response JSON is empty.")
                        except ValueError:
                            st.error(f"Response is not valid JSON. Raw response: {review_response.text}")
                    else:
                        st.error(f"Failed to review email. Status Code: {review_response.status_code}. Response: {review_response.text}")
                else:
                    st.error("Please upload the sales email template.")
           
            #Send Email
            if st.session_state.reviewed_email:
                st.header("Email Sending")
                subject = st.text_input("Subject", "Enhance your work with our products")
                body = st.text_area("Email Body", value=st.session_state.reviewed_email, height=300)

                if st.button("Send Email"):
                    if subject and body:
                        send_response = requests.post(f"{FASTAPI_URL}/send-email/", data={
                            "prospect_email": st.session_state.prospect_email,
                            "subject": subject,
                            "body": body
                        })

                        if send_response.status_code == 200:
                            st.success("Email sent successfully.")
                        else:
                            st.error(f"Failed to send email. Status Code: {send_response.status_code}. Response: {send_response.text}")
                    else:
                        st.error("Please provide a subject and body for the email.")

if __name__ == "__main__":
    main()
