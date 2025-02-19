import streamlit as st
import pdfplumber
from bs4 import BeautifulSoup
import re

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    return text

# Function to extract text from HTML
def extract_text_from_html(html_path):
    with open(html_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")
    return soup.get_text("\n", strip=True)

# Function to extract relevant product details and format them properly
def extract_product_details(text):
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
    return products

# Function to extract and clean product specifications
def format_product_details(product_text):
    lines = product_text.split("\n")
    title = lines[0]
    formatted_text = f"### **{title} - Custom Configuration**\n\n"
    for line in lines[1:]:
        if re.match(r"^[A-Za-z]+", line):  # Ensure it's a valid spec line
            parts = line.split(" ", 1)
            if len(parts) == 2:
                key, value = parts
                formatted_text += f"- **{key}**: {value}\n"
    return formatted_text

# Streamlit app
def main():
    st.title("📄 Dell Quote to ChannelOnline Formatter")
    uploaded_file = st.file_uploader("Upload your Dell Quote (PDF or HTML)", type=["pdf", "html", "htm"])

    if uploaded_file is not None:
        file_extension = uploaded_file.name.split(".")[-1].lower()
        if file_extension == "pdf":
            with open("temp.pdf", "wb") as f:
                f.write(uploaded_file.read())
            raw_text = extract_text_from_pdf("temp.pdf")
        else:
            with open("temp.html", "wb") as f:
                f.write(uploaded_file.read())
            raw_text = extract_text_from_html("temp.html")

        # Extract and format product details
        product_sections = extract_product_details(raw_text)
        formatted_outputs = [format_product_details(product) for product in product_sections]
        
        # Remove unnecessary sections (quote info, totals, terms, legal details)
        cleaned_output = "\n\n---\n\n".join(formatted_outputs)
        cleaned_output = re.sub(r".*(Quote No.|Total|Customer #|Terms of Sale|Shipping|Estimated Tax).*", "", cleaned_output)
        
        st.subheader("Formatted Output:")
        st.text_area("Copy and paste into ChannelOnline:", cleaned_output, height=600)
        st.download_button("Download Formatted Text", cleaned_output, file_name="formatted_specs.txt")

if __name__ == "__main__":
    main()
