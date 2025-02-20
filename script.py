import streamlit as st
import re

def format_input_data(raw_text):
    """Formats the pasted input data into a clean, professional output for ChannelOnline with improved spacing."""
    lines = raw_text.strip().split("\n")
    formatted_output = []
    
    # Extract and format data
    first_line = True
    base_name = ""
    for line in lines:
        parts = line.split("\t")  # Tab-separated columns
        if len(parts) >= 5:  # Ensure correct structure
            category = parts[0].strip()
            description = parts[1].strip()
            qty = parts[4].strip()
            
            if first_line:
                base_name = description
                formatted_output.append(f"### {base_name} CTO\n\n")
                first_line = False
            
            formatted_output.append(f"• {category}:  {description}  \n   **Quantity:** {qty}\n")
    
    return "\n".join(formatted_output)

# Streamlit App
def main():
    # Add Safari Micro logo with provided URL
    st.image("https://safarimicro.com/wp-content/uploads/2022/01/SafariMicro-Color-with-Solid-Icon-Copy.png", width=250)
    
    # Custom header with branding
    st.title("🚀 Safari Micro - Dell Quote Formatter")
    st.markdown("Transform your Dell Quotes into a ChannelOnline-ready format with ease!")
    
    raw_input = st.text_area("Paste your Dell Quote data here:", height=200)
    
    if st.button("Format Output"):
        if raw_input.strip():
            formatted_text = format_input_data(raw_input)
            st.subheader("📝 Formatted Output:")
            st.text_area("Copy and paste into ChannelOnline:", formatted_text, height=500)
            st.download_button("📥 Download Formatted Text", formatted_text, file_name="formatted_specs.txt")
        else:
            st.warning("⚠️ Please paste the Dell Quote data before formatting.")

if __name__ == "__main__":
    main()
