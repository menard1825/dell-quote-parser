import pdfplumber
import pytesseract
import pdf2image
import re
import streamlit as st

def extract_text_from_pdf(pdf_path):
    """Extracts text from PDF, using OCR if necessary."""
    text = ""

    # Try normal text extraction first
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"

    # If no text was found, use OCR
    if not text.strip():
        images = pdf2image.convert_from_path(pdf_path)
        for img in images:
            text += pytesseract.image_to_string(img) + "\n"

    return text

def separate_products(text):
    """Separates multiple Dell products in the quote."""
    products = []
    current_product = []
    
    lines = text.split("\n")
    
    for line in lines:
        # Detect a new product section (Base or Model Name)
        if re.search(r"(Base|Precision|Latitude|OptiPlex|Workstation)", line, re.IGNORECASE):
            if current_product:  # Save the previous product before starting a new one
                products.append("\n".join(current_product))
                current_product = []
        
        current_product.append(line)
    
    if current_product:
        products.append("\n".join(current_product))  # Add the last product
    
    return products

def extract_specs(text):
    """Parses extracted text to format each product's specs properly."""
    specs = []
    lines = text.split("\n")

    for line in lines:
        match = re.match(r"(.*?)\s{2,}(.*?)\s{2,}(\d+)", line)  # Adjusted regex for spec lines
        if match:
            category, description, qty = match.groups()
            specs.append(f"- **{category.strip()}**: {description.strip()} *(Qty: {qty})*")

    return "\n".join(specs)

def main():
    st.title("📄 Dell Quote PDF to ChannelOnline Formatter")
    uploaded_file = st.file_uploader("Upload your Dell Quote PDF", type=["pdf"])

    if uploaded_file is not None:
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.read())

        raw_text = extract_text_from_pdf("temp.pdf")
        product_sections = separate_products(raw_text)

        formatted_outputs = []
        for i, product_text in enumerate(product_sections):
            formatted_specs = extract_specs(product_text)
            formatted_outputs.append(f"### **Product {i+1}**\n{formatted_specs}\n")

        final_output = "\n---\n".join(formatted_outputs)

        st.subheader("Formatted Output:")
        st.text_area("Copy and paste into ChannelOnline:", final_output, height=600)
        st.download_button("Download Formatted Text", final_output, file_name="formatted_specs.txt")

if __name__ == "__main__":
    main()

