import datetime
import io
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pdfkit
import uuid
import os
from s3_handler import s3_handler_instance

# Create FastAPI app
app = FastAPI()

# Define input schema

PREFIX = 'html-to-pdf-'


class HTMLInput(BaseModel):
    html: str


# Output directory for PDFs
PDF_OUTPUT_DIR = "generated_pdfs"
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
    try:
        # Generate a unique filename
        filename = f"{uuid.uuid4()}.pdf"
        output_path = os.path.join(PDF_OUTPUT_DIR, filename)

        # Convert HTML to PDF
        data = pdfkit.from_string(
            input.html, output_path, configuration=PDFKIT_CONFIG)

        # Upload PDF to S3
        path = ''
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

        os.remove(output_path)

        # Return the filename
        return {"filename": filename_to_upload, "path": path}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating PDF: {str(e)}")
