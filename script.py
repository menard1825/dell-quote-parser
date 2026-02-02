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
    Formats text copied from the 'View in Browser' page of a Dell email quote.
    Handles both tab-separated lines (classic copy) and newline-separated lists.
    """
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

    # Regex to identify SKU lines (e.g., 210-BRXT or 5319-BBLZ)
    sku_regex = re.compile(r'^[A-Z0-9]{3,}-[A-Z0-9]{4,}')
    
    parsed_items = []
    
    # scan the lines. If we find a SKU, we assume the previous line was the description
    # and we look ahead for a quantity.
    for i, line in enumerate(lines):
        if sku_regex.match(line):
            # We found a SKU line. 
            # The Description is almost always the line immediately before it.
            if i > 0:
                description = lines[i-1]
                
                # Look ahead for quantity (it might be 1 or 2 lines down depending on formatting)
                qty = 1
                found_qty = False
                
                # Check the next 3 lines for a standalone number
                for offset in range(1, 4):
                    if i + offset < len(lines):
                        candidate = lines[i + offset]
                        # If it's a digit (like '2') and distinct from the next SKU or dashes
                        if candidate.isdigit():
                            qty = int(candidate)
                            found_qty = True
                            break
                        # Stop looking if we hit a text line that looks like a new description
                        if len(candidate) > 5 and not candidate.isdigit() and not candidate.startswith('-'):
                            break
                
                parsed_items.append({"desc": description, "qty": qty})

    if not parsed_items:
        return "Could not detect any products. Ensure you copied the Description, SKU, and Quantity columns."

    # Format the output
    output_lines = []
    
    # We assume the first item found is the "Base" unit for the header
    if parsed_items:
        base_item = parsed_items[0]
        output_lines.append(f"### {base_item['desc']}\n")
        
        # Determine base quantity from the first item
        base_qty = base_item['qty']

        # List all items (including the first one if you want, or skip it. 
        # Usually it's cleaner to list components below)
        for item in parsed_items[1:]:
            # Clean up description (remove 'Quantity: ' if it somehow got in there)
            clean_desc = item['desc'].replace("Quantity:", "").strip()
            
            # Logic to normalize quantity display
            display_qty = 1 if item['qty'] == base_qty else item['qty']
            
            output_lines.append(f"• {clean_desc} (Qty: {display_qty})")

    return "\n".join(output_lines)

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
    
    # Regex to find component lines
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
