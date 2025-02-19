import pdfplumber
import re
import streamlit as st
from bs4 import BeautifulSoup

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"

    return text if text.strip() else "⚠️ No text extracted from PDF."

def extract_text_from_html(html_content):
    """Extracts only product details from a Dell Quote HTML file."""
    soup = BeautifulSoup(html_content, "html.parser")
    extracted_text = ""

    # Find "Product Details" section
    for section in soup.find_all(["table", "div"]):
        if "Product Details" in section.get_text():
            extracted_text = section.get_text(separator=" | ", strip=True)
            break

    return extracted_text if extracted_text.strip() else "⚠️ 'Product Details' section not found in HTML."

def clean_text(text):
    """Removes pricing, SKUs, and irrelevant details."""
    ignore_keywords = [
        "Subtotal", "Taxable Amount", "Estimated Tax", "Shipping", "Order",
        "Sales Rep", "Quote", "Total", "Unit Price", "SKU", "Description",
        "Customer", "Phone", "Email", "JOHN LANNON", "SAFARI MICRO"
    ]
    
    lines = text.split("\n")
    cleaned_lines = [line for line in lines if not any(ignore in line for ignore in ignore_keywords)]
    
    return "\n".join(cleaned_lines) if cleaned_lines else "⚠️ No valid product details extracted."

def separate_products(text):
    """Separates multiple products in the quote."""
    products = []
    current_product = []

    product_keywords = ["Precision", "Latitude", "OptiPlex", "Workstation"]
    lines = text.split("\n")

    for line in lines:
        if any(keyword in line for keyword in product_keywords):
            if current_product:
                products.append("\n".join(current_product))
                current_product = []
        current_product.append(line.strip())

    if current_product:
        products.append("\n".join(current_product))

    return products if products else ["⚠️ No products detected."]

def extract_specs(product_text):
    """Formats product descriptions and quantities for ChannelOnline."""
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

    return "\n".join(formatted_specs) if len(formatted_specs) > 1 else "⚠️ No valid specs extracted."

def main():
    st.title("📄 Dell Quote Formatter (PDF & HTML)")

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

        st.subheader("🛠 Raw Extracted Text (Before Cleaning)")
        st.text_area("Raw Data:", extracted_text, height=300)

        extracted_text = clean_text(extracted_text)

        st.subheader("🛠 Cleaned Text (Before Formatting)")
        st.text_area("Cleaned Data:", extracted_text, height=300)

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
