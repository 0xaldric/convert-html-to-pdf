import datetime
import io
from fastapi import Body, FastAPI, HTTPException
from pydantic import BaseModel
import pdfkit
import uuid
import os
from s3_handler import s3_handler_instance
import logging

logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Create FastAPI app
app = FastAPI()

# Define input schema

PREFIX = 'html-to-pdf-'


class HTMLInput(BaseModel):
    html: str


# Output directory for PDFs
PDF_OUTPUT_DIR = "generated_pdfs"
HTML_OUTPUT_DIR = "generated_htmls"
# Create directory if it doesn't exist
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)

# PDFKit configuration (Path to wkhtmltopdf binary if needed)
PDFKIT_CONFIG = pdfkit.configuration(
    wkhtmltopdf='/usr/local/bin/wkhtmltopdf')  # Update path as necessary


@app.post("/generate-pdf")
async def generate_pdf(input: HTMLInput):
    """
    API endpoint to generate PDF from HTML using pdfkit.

    Args:
        input (HTMLInput): Input containing the HTML string.

    Returns:
        dict: Dictionary with the generated filename.
    """
    html = input.html
    return generate_pdf_and_upload(html)


def generate_pdf_and_upload(html):
    try:
        # Generate a unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        name = f"{timestamp}_{uuid.uuid4()}"
        filename = f"{name}.pdf"
        html_filename = f"{name}.html"
        text_filename = f"{name}.txt"
        output_path = os.path.join(PDF_OUTPUT_DIR, filename)
        html_output_path = os.path.join(HTML_OUTPUT_DIR, html_filename)
        text_output_path = os.path.join(HTML_OUTPUT_DIR, text_filename)

        with open(html_output_path, 'w') as html_file:
            html_file.write(html)

        with open(text_output_path, 'w') as text_file:
            text_file.write(html)

        with open(html_output_path, 'r') as html_file:
            content = html_file.read()

        # Convert HTML to PDF
        pdfkit.from_string(
            content, output_path, configuration=PDFKIT_CONFIG)

        # Upload PDF to S3
        path = ''
        html_path = ''
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        prefix = f"{PREFIX}{today}/"
        filename_to_upload = prefix+filename
        with open(output_path, 'rb') as pdf_file:
            path = s3_handler_instance.upload_file_data_to_s3(
                file_data=pdf_file,
                file_name=filename_to_upload
            )
            if not path:
                raise HTTPException(
                    status_code=500, detail="Failed to upload PDF to S3")
        html_filename_to_upload = prefix+html_filename
        with open(html_output_path, 'rb') as html_file:
            html_path = s3_handler_instance.upload_file_data_to_s3(
                file_data=html_file,
                file_name=html_filename_to_upload
            )
            if not html_path:
                raise HTTPException(
                    status_code=500, detail="Failed to upload HTML to S3")

        os.remove(output_path)
        os.remove(html_output_path)

        # Return the filename
        response = {"filename": filename_to_upload,
                    "path": path, "html_path": html_path}
        logging.info(f"Response: {response}")
        print(f"Response: {response}")
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating PDF: {str(e)}")


@app.post("/generate-pdf-submit-text")
async def receive_plain_text(content: str = Body(..., media_type="text/plain")):
    """_summary_

    Args:
        content (str, optional): _description_. Defaults to Body(..., media_type="text/plain").

    Returns:
        _type_: _description_
    """
    return generate_pdf_and_upload(content)
