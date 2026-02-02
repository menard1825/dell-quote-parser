import streamlit as st
import re

def format_premier_cto(raw_text):
    """
    Formats tab-separated data from Dell Premier into a clean, 
    professional output for ChannelOnline.
    """
    lines = raw_text.strip().split("\n")
    formatted_output = []
    current_product = []
    base_qty = 1

    for line in lines:
        parts = line.split("\t")
        if len(parts) >= 5:
            category = parts[0].strip()
            description = parts[1].strip()
            qty_str = parts[4].strip()
            qty = int(qty_str) if qty_str.isdigit() else 1

            if category.lower() == "base":
                if current_product:
                    formatted_output.append("\n".join(current_product))
                    formatted_output.append("\n")
                base_qty = qty
                current_product = [f"### {description} CTO\n"]
            elif category.lower() != "module":
                display_qty = 1 if qty == base_qty else qty
                current_product.append(f"• {category}: {description} (Qty: {display_qty})")
    
    if current_product:
        formatted_output.append("\n".join(current_product))
    
    return "\n".join(formatted_output)

def format_tdsynnex_cto(raw_text):
    """
    Formats data from a TDSynnex Dell CTO quote into a 
    ChannelOnline-friendly format.
    """
    lines = raw_text.strip().split("\n")
    formatted_output = []
    current_product = []
    is_base_product = False
    base_qty = 1
    
    for line in lines:
        parts = re.split(r'\s{2,}|\t+', line.strip())
        
        if len(parts) >= 3 and ("CTO" in parts[1] or "Mobile Precision" in parts[1]):
            if current_product:
                formatted_output.append("\n".join(current_product))
                formatted_output.append("\n")
            
            qty_str = parts[-1].strip()
            base_qty = int(qty_str) if qty_str.isdigit() else 1
            current_product = [f"### {parts[1]}\n"]
            is_base_product = True
        elif len(parts) >= 3 and is_base_product:
            description = " ".join(parts[1:-1]).strip()
            qty_str = parts[-1].strip()
            qty = int(qty_str) if qty_str.isdigit() else 1
            display_qty = 1 if qty == base_qty else qty
            current_product.append(f"• {description} (Qty: {display_qty})")
    
    if current_product:
        formatted_output.append("\n".join(current_product))
    
    return "\n".join(formatted_output)

def format_email_cto(raw_text):
    """
    Formats tab-separated text copied from the 'View in Browser' 
    page of a Dell email quote.
    """
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

    section_starts = []
    for i, line in enumerate(lines):
        if "Description" in line and "SKU" in line and "Quantity" in line:
            section_starts.append(i + 1)

    if not section_starts:
        return "Could not find any product detail sections."

    all_formatted_products = []
    
    for i in range(len(section_starts)):
        start_index = section_starts[i]
        end_index = section_starts[i+1] - 1 if i + 1 < len(section_starts) else len(lines)
        section_lines = lines[start_index:end_index]

        current_product_components = []
        # UPDATED: Changed {3} to {3,} to allow SKUs like 5319-BBLZ
        sku_regex = re.compile(r'^[A-Z0-9]{3,}-[A-Z0-9]{4,}$')
        base_qty = 1

        for line in section_lines:
            parts = re.split(r'\t+', line)
            
            if len(parts) >= 2 and sku_regex.match(parts[1].strip()):
                desc = parts[0].strip()
                
                qty_str = "1"
                if len(parts) >= 4 and parts[3].strip().isdigit():
                    qty_str = parts[3].strip()
                qty = int(qty_str)

                if not current_product_components:
                    base_qty = qty
                    current_product_components.append(f"### {desc}\n")
                else:
                    display_qty = 1 if qty == base_qty else qty
                    current_product_components.append(f"• {desc} (Qty: {display_qty})")

        if current_product_components:
            all_formatted_products.append("\n".join(current_product_components))

    return "\n\n".join(all_formatted_products)

def format_generic_cto(raw_text):
    """
    Formats a generic, unstructured Dell CTO quote.
    """
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    
    # Find the base product name (usually the first line)
    product_name = lines[0] if lines else "Dell CTO Product"

    # Find the base quantity
    base_qty = 0
    for line in lines:
        # Look for a number that's likely the quantity (e.g., "50")
        match = re.search(r'-(\d+)-', line)
        if match:
            qty = int(match.group(1))
            if qty > base_qty:
                base_qty = qty

    if base_qty == 0:
        base_qty = 1

    formatted_output = [f"### {product_name}\n"]
    
    # UPDATED: Changed \w{3} to \w{3,} to allow longer SKU prefixes
    component_regex = re.compile(r'(.+?)(\w{3,}-\w{4,}-\d+-\d+)')

    for line in lines:
        match = component_regex.match(line)
        if match:
            description = match.group(1).strip()
            sku_part = match.group(2)
            
            # Extract quantity from the SKU part
            qty_match = re.search(r'-(\d+)$', sku_part)
            qty = int(qty_match.group(1)) if qty_match else 1
            
            display_qty = 1 if qty == base_qty else qty
            formatted_output.append(f"• {description} (Qty: {display_qty})")

    return "\n".join(formatted_output)

def main():
    """
    Main function to run the Streamlit application.
    """
    st.image("https://safarimicro.com/wp-content/uploads/2022/01/SafariMicro-Color-with-Solid-Icon-Copy.png", width=250)
    st.title("🚀 Safari Micro - Dell Quote Formatter")
    st.markdown("Transform your Dell Quotes into a ChannelOnline-ready format with ease!")
    
    format_type = st.radio(
        "Select Dell CTO Input Type:", 
        ["Dell Premier CTO", "TDSynnex Dell CTO", "Dell Email CTO", "Generic CTO"]
    )
    
    raw_input = st.text_area("Paste your Dell Quote data here:", height=300)
    
    if st.button("Format Output"):
        if raw_input.strip():
            if format_type == "Dell Premier CTO":
                formatted_text = format_premier_cto(raw_input)
            elif format_type == "TDSynnex Dell CTO":
                formatted_text = format_tdsynnex_cto(raw_input)
            elif format_type == "Dell Email CTO":
                formatted_text = format_email_cto(raw_input)
            else:
                formatted_text = format_generic_cto(raw_input)
                
            st.subheader("📝 Formatted Output:")
            st.text_area("Copy and paste into ChannelOnline:", formatted_text, height=500)
            st.download_button("📥 Download Formatted Text", formatted_text, file_name="formatted_specs.txt")
        else:
            st.warning("⚠️ Please paste the Dell Quote data before formatting.")

if __name__ == "__main__":
    main()
