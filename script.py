import streamlit as st
import re

def format_input_data(raw_text):
    """Formats the pasted input data into a clean, professional output for multiple products in ChannelOnline."""
    lines = raw_text.strip().split("\n")
    formatted_output = []
    
    current_product = []
    current_product_name = None
    
    for line in lines:
        parts = line.split("\t")  # Handle tab-separated format
        
        if len(parts) == 1 and not line.startswith(" ") and not line.startswith("\t") and not parts[0].isdigit():
            # This is likely the product title line (new format) if it's not a number
            if current_product:
                formatted_output.append("\n".join(current_product))
                formatted_output.append("\n")
            current_product_name = line.strip()
            current_product = [f"### {current_product_name} CTO\n"]
            continue
        
        if len(parts) >= 3:  # Adjusting to capture both formats
            if len(parts) == 5:  # Old format (Module, Description, Product Code, SKU, Qty)
                category = parts[0].strip()
                description = parts[1].strip()
                qty = parts[4].strip()
            elif len(parts) == 3:  # New format (SKU, Description, Qty)
                category = ""
                description = parts[1].strip()
                qty = parts[2].strip()
            else:
                continue  # Skip malformed lines
            
            if category.lower() == "base" or category.lower() == "module":
                if current_product:
                    formatted_output.append("\n".join(current_product))
                    formatted_output.append("\n")
                current_product = [f"### {description} CTO\n"]
            elif category and category.lower() != "module":  # Exclude unwanted module line
                current_product.append(f"• {category}: {description} (Qty: {qty})")
            else:
                current_product.append(f"• {description} (Qty: {qty})")
    
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
