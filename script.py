import pdfplumber
import re
import streamlit as st

def extract_text_from_pdf(pdf_path):
    """Extracts text from PDF."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    return text

def separate_products(text):
    """Separates multiple Dell products in the quote."""
    products = []
    current_product = []
    
    lines = text.split("\n")
    
    for line in lines:
        # Detect new product section (Base Model Name)
        if re.search(r"(Precision|Latitude|OptiPlex|Workstation)", line, re.IGNORECASE):
            if current_product:
                products.append("\n".join(current_product))
                current_product = []
        current_product.append(line)
    
    if current_product:
        products.append("\n".join(current_product))
    
    return products

def extract_specs(product_text):
    """Extracts and formats only descriptions and quantities."""
    lines = product_text.split("\n")
    formatted_specs = []
    
    # Detect product title
    product_title = "Unknown Product"
    for line in lines:
        match_title = re.search(r"(Precision|Latitude|OptiPlex|Workstation) .*", line, re.IGNORECASE)
        if match_title:
            product_title = match_title.group(0).strip()
            break

    formatted_specs.append(f"### **{product_title} - Custom Configuration**\n")

    for line in lines:
        # Extract only description and quantity
        match = re.match(r"(.+?)\s{2,}(\d+)$", line)
        if match:
            description, qty = match.groups()
            formatted_specs.append(f"- **{description.strip()}** *(Qty: {qty})*")

    return "\n".join(formatted_specs)

def main():
    st.title("📄 Dell Quote PDF to ChannelOnline Formatter")
    uploaded_file = st.file_uploader("Upload your Dell Quote PDF", type=["pdf"])

    if uploaded_file is not None:
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.read())

        raw_text = extract_text_from_pdf("temp.pdf")
        product_sections = separate_products(raw_text)

        formatted_outputs = []
        for product_text in product_sections:
            formatted_specs = extract_specs(product_text)
            if formatted_specs:
                formatted_outputs.append(formatted_specs)

        final_output = "\n\n---\n\n".join(formatted_outputs)

        st.subheader("Formatted Output:")
        st.text_area("Copy and paste into ChannelOnline:", final_output, height=600)
        st.download_button("Download Formatted Text", final_output, file_name="formatted_specs.txt")

if __name__ == "__main__":
    main()
