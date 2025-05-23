#gmail_integration.py

import os
import base64
import io
from email import message_from_bytes
from email.message import EmailMessage
from fpdf import FPDF
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from evaluator import evaluate_mte
from utils import extract_mte_data
from config import CONFIG, ENV
from datetime import datetime
from fpdf.enums import XPos, YPos

# Get environment-specific configuration
central_authority_email = CONFIG[ENV]["central_authority_email"]
user_id = CONFIG[ENV]["user_id"]

SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/drive.file'
]

def authenticate_services():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    gmail_service = build('gmail', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    return gmail_service, drive_service

def get_unread_messages(service):
    try:
        response = service.users().messages().list(userId=user_id, labelIds=['INBOX'], q="is:unread").execute()
        return response.get('messages', [])
    except Exception as error:
        print(f'Error fetching messages: {error}')
        return []

def get_message(service, msg_id):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()
        msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
        return message_from_bytes(msg_str)
    except Exception as error:
        print(f'Error fetching message: {error}')
        return None

def mark_as_read(service, msg_id):
    try:
        service.users().messages().modify(
            userId=user_id,
            id=msg_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
    except Exception as error:
        print(f'Error marking message as read: {error}')

def save_attachment(mime_msg, download_folder):
    for part in mime_msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        filename = part.get_filename()
        if filename and filename.endswith('.xlsx'):
            os.makedirs(download_folder, exist_ok=True)
            filepath = os.path.join(download_folder, filename)
            with open(filepath, 'wb') as f:
                f.write(part.get_payload(decode=True))
            return filepath
    return None



def generate_pdf(feedback, pdf_path):
    # Extract relevant data
    section_scores = feedback.get("section_scores", {})
    strengths = feedback.get("strengths", [])
    areas_for_improvement = feedback.get("areas_for_improvement", [])
    suggestions = feedback.get("suggestions", [])

    # Metadata
    student_name = feedback.get("student_name", "N/A")
    submission_month = feedback.get("submission_month", "N/A")
    college_name = feedback.get("college_name", "N/A")
    student_class = feedback.get("class_info", "N/A")
    generation_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    # Initialize PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    font_path = 'fonts/DejaVuSans.ttf'
    font_path_bold = 'fonts/DejaVuSans-Bold.ttf'
    if not os.path.exists(font_path):
        print(f"Font file not found at {font_path}.")
        return
    pdf.add_font('DejaVu', '', font_path)
    pdf.add_font('DejaVu', 'B', font_path_bold)
    pdf.set_font('DejaVu', '', 16)

    # Title
    pdf.cell(0, 10, "MTE Evaluation Report", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(10)
    pdf.set_font("DejaVu", '', 12)

    # Student details
    student_details = [
        f"Name of the Student: {student_name}",
        f"Submission Month: {submission_month}",
        f"College Name: {college_name}",
        f"Class: {student_class}",
        f"PDF Generated On: {generation_date}"
    ]
    for line in student_details:
        pdf.multi_cell(0, 8, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(5)

    # Utility function for bullets
    def add_bullet_section(title, items):
        if not items:
            return
        pdf.set_font("DejaVu", 'B', 12)
        pdf.cell(0, 10, f"{title}:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("DejaVu", '', 12)
        for item in items:
            if max((len(w) for w in item.split()), default=0) > 80:
                pdf.set_font("DejaVu", '', 10)
                pdf.multi_cell(0, 8, f"• {item}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.set_font("DejaVu", '', 12)
            else:
                pdf.multi_cell(0, 8, f"• {item}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(3)

    # Add bullet sections
    add_bullet_section("Strengths", strengths)
    add_bullet_section("Areas for Improvement", areas_for_improvement)
    add_bullet_section("Suggestions", suggestions)

    # Section-wise Scores
    if section_scores:
        pdf.set_font("DejaVu", 'B', 12)
        pdf.cell(0, 10, "Section-wise Evaluation:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("DejaVu", '', 12)
        pdf.ln(3)
        for section, details in section_scores.items():
            section_title = section.replace("_", " ").title()
            pdf.set_font("DejaVu", 'B', 12)
            pdf.cell(0, 10, f"{section_title} (Score: {details['score']})", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("DejaVu", '', 12)
            lines = [
                f"• Reason: {details['reason']}",
                f"• Feedback: {details['feedback']}",
                f"• Suggestions: {details['suggestions']}"
            ]
            for line in lines:
                if not line.strip():
                    continue
                if max((len(word) for word in line.split()), default=0) > 80:
                    pdf.set_font("DejaVu", '', 10)
                    pdf.multi_cell(0, 8, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.set_font("DejaVu", '', 12)
                else:
                    pdf.multi_cell(0, 8, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(3)

    # Save PDF
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    pdf.output(pdf_path)




def send_email_with_attachment(service, to, cc, subject, body_text, file_path):
    message = EmailMessage()
    message['To'] = to
    if cc:
        message['Cc'] = cc
    message['From'] = user_id
    message['Subject'] = subject
    message.set_content(body_text)

    with open(file_path, 'rb') as f:
        file_data = f.read()
        file_name = os.path.basename(file_path)
    message.add_attachment(file_data, maintype='application', subtype='pdf', filename=file_name)

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {'raw': encoded_message}
    send_message = service.users().messages().send(userId=user_id, body=create_message).execute()
    print(f'Message sent. ID: {send_message["id"]}')

def create_folder(service, name, parent_id=None):
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        file_metadata['parents'] = [parent_id]
    folder = service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')

def search_folder(service, name, parent_id=None):
    query = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    files = results.get('files', [])
    return files[0]['id'] if files else None

def upload_file(service, file_path, folder_id):
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')




def main():
    gmail_service, drive_service = authenticate_services()
    messages = get_unread_messages(gmail_service)
    print(f'Found {len(messages)} unread messages.')

    mte_folder_id = search_folder(drive_service, 'MTE_Submissions')
    if not mte_folder_id:
        mte_folder_id = create_folder(drive_service, 'MTE_Submissions')

    for msg in messages:
        mime_msg = get_message(gmail_service, msg['id'])
        if not mime_msg:
            continue

        sender = mime_msg['From']
        subject = mime_msg['Subject']
        raw_cc = mime_msg.get_all('Cc', [])
        cc_emails = []

        if raw_cc:
            for item in raw_cc:
                cc_emails.extend([addr.strip() for addr in item.split(',')])

        student_email = sender.split('<')[-1].strip('>') if '<' in sender else sender.strip()
        mentor_emails = [email for email in cc_emails if email.lower() != central_authority_email.lower()]
        print(f'Processing email from {student_email} | Subject: {subject} | Mentors: {mentor_emails}')

        attachment_path = save_attachment(mime_msg, 'downloads')
        if attachment_path:
            print(f'Attachment saved: {attachment_path}')
            mte_data = extract_mte_data(attachment_path)

            # Extract student metadata
            student_name = mte_data.get("student_name", "N/A")
            submission_month = mte_data.get("submission_month", "N/A")
            college_name = mte_data.get("college_name", "N/A")
            student_class = mte_data.get("class_info", "N/A")

            # Evaluate and enrich feedback
            feedback = evaluate_mte(mte_data, selected_model='deepseek-r1-distill-llama-70b')

            feedback.update({
                "student_name": student_name,
                "submission_month": submission_month,
                "college_name": college_name,
                "class_info": student_class
            })

            # Create student folder if not exists
            student_folder_id = search_folder(drive_service, student_email, parent_id=mte_folder_id)
            if not student_folder_id:
                student_folder_id = create_folder(drive_service, student_email, parent_id=mte_folder_id)

            # Generate PDF path
            pdf_filename = os.path.splitext(os.path.basename(attachment_path))[0] + '_feedback.pdf'
            pdf_path = os.path.join('reports', pdf_filename)

            # Generate PDF
            generate_pdf(feedback, pdf_path)
            print(f'Generated PDF: {pdf_path}')

            # Upload both original and feedback
            upload_file(drive_service, attachment_path, student_folder_id)
            upload_file(drive_service, pdf_path, student_folder_id)

            # Prepare metadata for email body using variables, not feedback.get()
            metadata_text = f"""
Name of the Student: {student_name}
Submission Month: {submission_month}
College Name: {college_name}
Class: {student_class}
Report generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}
"""

            # Send to Student
            student_body_text = f"""Dear {student_name},

Please find your MTE Feedback Report attached.

Here are your details:
{metadata_text}

Regards,
Guruji Foundation
"""
            send_email_with_attachment(
                service=gmail_service,
                to=student_email,
                cc="",
                subject='MTE Feedback Report',
                body_text=student_body_text,
                file_path=pdf_path
            )

            # Send to Mentor
            if mentor_emails:
                mentor_body_text = f"""Dear Mentor,

Please find your student's MTE Feedback Report attached.

Student Details:
{metadata_text}

Regards,
Guruji Foundation
"""
                send_email_with_attachment(
                    service=gmail_service,
                    to=", ".join(mentor_emails),
                    cc="",
                    subject='MTE Feedback Report of Your Student',
                    body_text=mentor_body_text,
                    file_path=pdf_path
                )

            mark_as_read(gmail_service, msg['id'])

        else:
            print('No valid Excel file found in the email.')


if __name__ == '__main__':
    main()
