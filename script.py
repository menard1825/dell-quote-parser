import streamlit as st
import re

def format_premier_cto(raw_text):
    """Formats the pasted input data into a clean, professional output for multiple products in ChannelOnline."""
    lines = raw_text.strip().split("\n")
    formatted_output = []
    current_product = []
    is_base_product = False
    
    for line in lines:
        line = line.strip()
        
        # Detect base product name
        if re.match(r'^(Mobile Precision|Dell Mobile Precision Workstation) \d+', line):
            if current_product:
                formatted_output.append("\n".join(current_product))
                formatted_output.append("\n")
            current_product = [f"### {line} CTO\n"]
            is_base_product = True
        
        # Ignore price-related lines
        elif re.search(r'^(\$|Estimated delivery|Subtotal|Unit Price|Total|Description|SKU)', line, re.IGNORECASE):
            continue
        
        # Extract component details
        else:
            parts = re.split(r'\s{2,}|\t+', line)
            if len(parts) >= 2 and is_base_product:
                description = " ".join(parts[:-1]).strip()
                qty = parts[-1].strip()
                if qty.isdigit():
                    current_product.append(f"• {description} (Qty: {qty})")
    
    if current_product:
        formatted_output.append("\n".join(current_product))
    
    return "\n".join(formatted_output)

def format_tdsynnex_cto(raw_text):
    """Formats input data from TDSynnex Dell CTO to a ChannelOnline-friendly format."""
    lines = raw_text.strip().split("\n")
    formatted_output = []
    current_product = []
    is_base_product = False
    
    for line in lines:
        parts = re.split(r'\s{2,}|\t+', line.strip())
        
        if len(parts) >= 2 and ("CTO" in parts[1] or "Mobile Precision" in parts[1]):
            # Base product detected
            if current_product:
                formatted_output.append("\n".join(current_product))
                formatted_output.append("\n")
            current_product = [f"### {parts[1]}\n"]  # Removed SKU
            is_base_product = True
        elif len(parts) >= 2 and is_base_product:
            # Extract description and quantity only
            description = " ".join(parts[:-1]).strip()
            qty = parts[-1].strip()
            current_product.append(f"• {description} (Qty: {qty})")
    
    if current_product:
        formatted_output.append("\n".join(current_product))
    
    return "\n".join(formatted_output)

def main():
    st.image("https://safarimicro.com/wp-content/uploads/2022/01/SafariMicro-Color-with-Solid-Icon-Copy.png", width=250)
    st.title("🚀 Safari Micro - Dell Quote Formatter")
    st.markdown("Transform your Dell Quotes into a ChannelOnline-ready format with ease!")
    
    format_type = st.radio("Select Dell CTO Input Type:", ["Dell Premier CTO", "TDSynnex Dell CTO"])
    
    raw_input = st.text_area("Paste your Dell Quote data here:", height=300)
    
    if st.button("Format Output"):
        if raw_input.strip():
            if format_type == "Dell Premier CTO":
                formatted_text = format_premier_cto(raw_input)
            else:
                formatted_text = format_tdsynnex_cto(raw_input)
                
            st.subheader("📝 Formatted Output:")
            st.text_area("Copy and paste into ChannelOnline:", formatted_text, height=500)
            st.download_button("📥 Download Formatted Text", formatted_text, file_name="formatted_specs.txt")
        else:
            st.warning("⚠️ Please paste the Dell Quote data before formatting.")

if __name__ == "__main__":
    main()
