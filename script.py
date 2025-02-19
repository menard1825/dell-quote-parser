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

# Function to extract product details, SKU, and quantity
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

# Function to extract SKU-Quantity pairs
def extract_sku_quantity_pairs(soup):
    sku_quantity_mapping = {}
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 5:
                description = cells[0].get_text(strip=True)
                sku = cells[1].get_text(strip=True)
                quantity = cells[4].get_text(strip=True)
                if sku and quantity.isdigit():
                    sku_quantity_mapping[description] = {"sku": sku, "quantity": int(quantity)}
    return sku_quantity_mapping

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

        # Extract product details
        product_sections = extract_product_details(raw_text)
        formatted_outputs = []
        for product_text in product_sections:
            formatted_outputs.append(f"### **{product_text.split('\n')[0]} - Custom Configuration**\n" + "\n".join(product_text.split("\n")[1:]))

        final_output = "\n\n---\n\n".join(formatted_outputs)
        
        st.subheader("Formatted Output:")
        st.text_area("Copy and paste into ChannelOnline:", final_output, height=600)
        st.download_button("Download Formatted Text", final_output, file_name="formatted_specs.txt")

if __name__ == "__main__":
    main()
