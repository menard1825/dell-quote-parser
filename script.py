import pdfplumber
import re
import streamlit as st

def extract_specs_from_pdf(pdf_path):
    specs = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split("\n")
                for line in lines:
                    # Match module descriptions (Processor, Memory, Storage, etc.)
                    match = re.match(r"(.*?)\s{2,}(.*?)\s{2,}(\d+)", line)
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
        
        formatted_specs = extract_specs_from_pdf("temp.pdf")
        
        st.subheader("Formatted Output:")
        st.text_area("Copy and paste into ChannelOnline:", formatted_specs, height=400)
        
        st.download_button("Download Formatted Text", formatted_specs, file_name="formatted_specs.txt")

if __name__ == "__main__":
    main()
