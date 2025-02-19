import pdfplumber
import re
import streamlit as st
from bs4 import BeautifulSoup

def extract_text_from_pdf(pdf_path):
    """Extracts text from PDF."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    
    if not text.strip():
        return "⚠️ No text was extracted from the PDF. Check if it's a scanned document."
    
    return text

def extract_text_from_html(html_content):
    """Extracts relevant text from an HTML file (only descriptions & quantities)."""
    soup = BeautifulSoup(html_content, "html.parser")
    extracted_text = ""

    # Debug: Print full HTML structure
    print(soup.prettify())

    for row in soup.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) >= 2:  # Ensure at least description + quantity
            description = cols[0].get_text(strip=True)
            qty = cols[-1].get_text(strip=True)  # Quantity is usually in the last column

            # Ensure qty is a number and description is valid
            if description.lower() not in ["description", "qty", "quantity"] and qty.isdigit():
                extracted_text += f"{description}  {qty}\n"

    if not extracted_text.strip():
        return "⚠️ No valid text extracted from HTML. Check the file structure."
    
    return extracted_text

def clean_text(text):
    """Removes pricing, SKUs, and unnecessary text."""
    cleaned_lines = []
    for line in text.split("\n"):
        # Remove lines containing prices ($), SKU-like patterns (e.g., 210-BLLB), or dashes
        if not re.search(r"\$\d+|\d{2,}-\w{2,}|^-+$", line):
            cleaned_lines.append(line)
    
    if not cleaned_lines:
        return "⚠️ No clean text was extracted. Check if important details were removed."
    
    return "\n".join(cleaned_lines)

def separate_products(text):
    """Separates multiple Dell products in the quote."""
    products = []
    current_product = []
    
    lines = text.split("\n")
    
    for line in lines:
        if re.search(r"(Precision|Latitude|OptiPlex|Workstation)", line, re.IGNORECASE):
            if current_product:
                products.append("\n".join(current_product))
                current_product = []
        current_product.append(line)
    
    if current_product:
        products.append("\n".join(current_product))

    if not products:
        return ["⚠️ No products detected. Check extracted text."]
    
    return products

def extract_specs(product_text):
    """Extracts and formats only descriptions and quantities."""
    lines = product_text.split("\n")
    formatted_specs = []

    product_title = None
    for line in lines:
        match_title = re.search(r"(Precision|Latitude|OptiPlex|Workstation) .*", line, re.IGNORECASE)
        if match_title:
            product_title = match_title.group(0).strip()
            break

    if not product_title:
        return "⚠️ No product title found."

    formatted_specs.append(f"### **{product_title} - Custom Configuration**\n")

    for line in lines:
        match = re.match(r"(.+?)\s{2,}(\d+)$", line)
        if match:
            description, qty = match.groups()
            formatted_specs.append(f"- **{description.strip()}** *(Qty: {qty})*")

    if len(formatted_specs) == 1:
        return "⚠️ No valid specs extracted."

    return "\n".join(formatted_specs)

def main():
    st.title("📄 Dell Quote Formatter (PDF & HTML) - Debug Mode")

    uploaded_file = st.file_uploader("Upload your Dell Quote (PDF or HTML)", type=["pdf", "html"])

    if uploaded_file is not None:
        file_type = uploaded_file.type
        extracted_text = ""

        if file_type == "application/pdf":
            with open("temp.pdf", "wb") as f:
                f.write(uploaded_file.read())
            extracted_text = extract_text_from_pdf("temp.pdf")

        elif file_type == "text/html":
            extracted_text = extract_text_from_html(uploaded_file.getvalue().decode("utf-8"))

        # Debug: Show raw extracted text
        st.subheader("🛠 Raw Extracted Text (Before Cleaning)")
        st.text_area("Raw Data:", extracted_text, height=300)

        # Clean text (remove prices and SKUs)
        extracted_text = clean_text(extracted_text)

        # Debug: Show cleaned text
        st.subheader("🛠 Cleaned Text (Before Formatting)")
        st.text_area("Cleaned Data:", extracted_text, height=300)

        # Process and format the extracted text
        product_sections = separate_products(extracted_text)

        formatted_outputs = []
        for product_text in product_sections:
            formatted_specs = extract_specs(product_text)
            formatted_outputs.append(formatted_specs)

        final_output = "\n\n---\n\n".join(formatted_outputs)

        st.subheader("📌 Formatted Output for ChannelOnline")
        st.text_area("Copy and paste into ChannelOnline:", final_output, height=600)
        st.download_button("Download Formatted Text", final_output, file_name="formatted_specs.txt")

if __name__ == "__main__":
    main()
