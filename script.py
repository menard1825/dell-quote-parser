import streamlit as st
import re

def format_dell_premier_data(raw_text):
    """Formats the Dell Premier pasted input data into a clean, professional output for ChannelOnline."""
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
        
        if len(parts) >= 3:
            if len(parts) == 5:  # Dell Premier format (Module, Description, Product Code, SKU, Qty)
                category = parts[0].strip()
                description = parts[1].strip()
                qty = parts[4].strip()
            else:
                continue  # Skip malformed lines
            
            if category.lower() == "base" or category.lower() == "module":
                if current_product:
                    formatted_output.append("\n".join(current_product))
                    formatted_output.append("\n")
                current_product = [f"### {description} CTO\n"]
            elif category and category.lower() != "module":
                current_product.append(f"• {category}: {description} (Qty: {qty})")
            else:
                current_product.append(f"• {description} (Qty: {qty})")
    
    if current_product:
        formatted_output.append("\n".join(current_product))
    
    return "\n".join(formatted_output)

def format_td_synnex_data(raw_text):
    """Formats the TD Synnex CTO pasted input data into a clean, professional output for ChannelOnline."""
    lines = raw_text.strip().split("\n")
    formatted_output = []
    
    current_product = []
    current_product_name = None
    
    for line in lines:
        parts = line.split("\t")
        
        if len(parts) == 2 and not line.startswith(" ") and not line.startswith("\t"):  # Product Title
            if current_product:
                formatted_output.append("\n".join(current_product))
                formatted_output.append("\n")
            current_product_name = parts[0].strip()
            current_product = [f"### {current_product_name} CTO\n"]
            continue
        
        if len(parts) == 3:  # TD Synnex format (SKU, Description, Qty)
            description = parts[1].strip()
            qty = parts[2].strip()
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
    
    # User chooses format type
    format_type = st.radio("Select Quote Format:", ["Dell Premier", "TD Synnex CTO"])
    
    raw_input = st.text_area("Paste your Dell Quote data here:", height=300)
    
    if st.button("Format Output"):
        if raw_input.strip():
            if format_type == "Dell Premier":
                formatted_text = format_dell_premier_data(raw_input)
            else:
                formatted_text = format_td_synnex_data(raw_input)
            
            st.subheader("📝 Formatted Output:")
            st.text_area("Copy and paste into ChannelOnline:", formatted_text, height=500)
            st.download_button("📥 Download Formatted Text", formatted_text, file_name="formatted_specs.txt")
        else:
            st.warning("⚠️ Please paste the Dell Quote data before formatting.")

if __name__ == "__main__":
    main()
