import streamlit as st
import re

def format_input_data(raw_text):
    """Formats the pasted input data into a clean, professional output for multiple products in ChannelOnline."""
    lines = raw_text.strip().split("\n")
    formatted_output = []
    
    current_product = []
    for line in lines:
        parts = line.split("\t")  # Tab-separated columns
        if len(parts) >= 5:  # Ensure correct structure
            category = parts[0].strip()
            description = parts[1].strip()
            qty = parts[4].strip()
            
            # Detecting new product based on 'Base' keyword
            if category.lower() == "base":
                if current_product:
                    formatted_output.append("\n".join(current_product))
                    formatted_output.append("\n")  # Remove unnecessary separator
                current_product = [f"### {description} CTO\n"]
            elif category.lower() != "module":  # Exclude unwanted module line
                current_product.append(f"• {category}: {description} (Qty: {qty})")
    
    if current_product:
        formatted_output.append("\n".join(current_product))
    
    return "\n".join(formatted_output)

# Streamlit App
def main():
    # Add Safari Micro logo with provided URL
    st.image("https://safarimicro.com/wp-content/uploads/2022/01/SafariMicro-Color-with-Solid-Icon-Copy.png", width=250)
    
    # Custom header with branding
    st.title("🚀 Safari Micro - Dell Quote Formatter")
    st.markdown("Transform your Dell Quotes into a ChannelOnline-ready format with ease!")
    
    # Add instructional images
    st.image("https://safarimicro.com/wp-content/uploads/2022/01/Screenshot-Example.jpg", caption="Select and copy the highlighted text in the image above, then paste it below.", use_container_width=True)
    st.image("https://safarimicro.com/wp-content/uploads/2022/01/Screenshot-Alternative.jpg", caption="Alternative view for selecting the correct text.", use_container_width=True)
    
    raw_input = st.text_area("Paste your Dell Quote data here:", height=300)
    
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
