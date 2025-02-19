import streamlit as st
import re

def format_input_data(raw_text):
    """Formats the pasted input data into a clean output for ChannelOnline with bullet points."""
    lines = raw_text.strip().split("\n")
    formatted_output = []
    
    # Extract and format data
    first_line = True
    for line in lines:
        parts = line.split("\t")  # Tab-separated columns
        if len(parts) >= 5:  # Ensure correct structure
            category = parts[0].strip()
            description = parts[1].strip()
            qty = parts[4].strip()
            
            if first_line:
                formatted_output.append(f"### **{description} - Custom Configuration**\n")
                first_line = False
            
            formatted_output.append(f"• **{category}**: {description} (Qty: {qty})")
    
    return "\n".join(formatted_output)

# Streamlit App
def main():
    st.title("📄 Dell Quote to ChannelOnline Formatter")
    raw_input = st.text_area("Paste your Dell Quote data here:")
    
    if st.button("Format Output"):
        if raw_input.strip():
            formatted_text = format_input_data(raw_input)
            st.subheader("Formatted Output:")
            st.text_area("Copy and paste into ChannelOnline:", formatted_text, height=400)
            st.download_button("Download Formatted Text", formatted_text, file_name="formatted_specs.txt")
        else:
            st.warning("Please paste the Dell Quote data before formatting.")

if __name__ == "__main__":
    main()
