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

    for line in lines:
        # Expects tab-separated columns
        parts = line.split("\t")
        if len(parts) >= 5:  # Ensure the line has the expected structure
            category = parts[0].strip()
            description = parts[1].strip()
            qty = parts[4].strip()
            
            # "Base" indicates the start of a new product configuration
            if category.lower() == "base":
                if current_product:
                    formatted_output.append("\n".join(current_product))
                    formatted_output.append("\n") # Add a space between products
                current_product = [f"### {description} CTO\n"]
            # "Module" lines are usually headers and can be ignored
            elif category.lower() != "module":
                current_product.append(f"• {category}: {description} (Qty: {qty})")
    
    # Append the last product in the list
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
    
    for line in lines:
        # Split on multiple spaces or tabs to handle less structured input
        parts = re.split(r'\s{2,}|\t+', line.strip())
        
        # Detect the base product line
        if len(parts) >= 3 and ("CTO" in parts[1] or "Mobile Precision" in parts[1]):
            if current_product:
                formatted_output.append("\n".join(current_product))
                formatted_output.append("\n")
            current_product = [f"### {parts[1]}\n"]
            is_base_product = True
        # Process component lines that belong to the base product
        elif len(parts) >= 3 and is_base_product:
            description = " ".join(parts[1:-1]).strip()
            qty = parts[-1].strip()
            current_product.append(f"• {description} (Qty: {qty})")
    
    if current_product:
        formatted_output.append("\n".join(current_product))
    
    return "\n".join(formatted_output)

def format_email_cto(raw_text):
    """
    Formats input data from a copied Dell Email Quote to a 
    ChannelOnline-friendly format. This version is designed to handle
    pasted text where components are on multiple lines.
    """
    # Step 1: Clean up the input text using splitlines() for better line ending handling.
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    
    # Step 2: Define regex for SKU and filter out common table headers.
    sku_regex = re.compile(r'^[A-Z0-9]{3}-[A-Z0-9]{4,}$')
    headers = ["description", "sku", "unit price", "quantity"]
    lines = [line for line in lines if line.lower() not in headers]

    # Step 3: Find the indices of all lines that look like SKUs. This is our anchor.
    sku_indices = [i for i, line in enumerate(lines) if sku_regex.match(line)]

    if not sku_indices:
        return "" # Return blank if no SKUs found, avoids showing an error for empty input.

    # Step 4: Group lines into components based on SKU locations.
    components = []
    start_index = 0
    for sku_index in sku_indices:
        # A component block is SKU, then '-', then Qty. Check if this block is valid.
        if sku_index + 2 < len(lines) and lines[sku_index + 1].strip() == '-':
            try:
                qty = int(lines[sku_index + 2])
                
                # Description is all non-component lines since the last component.
                description_lines = lines[start_index:sku_index]
                description = " ".join(description_lines).strip()
                
                # A component with no description is usually not a real item.
                if not description:
                    start_index = sku_index + 3
                    continue

                components.append({
                    'description': description,
                    'sku': lines[sku_index],
                    'qty': qty
                })
                
                # The next description will start after this component block.
                start_index = sku_index + 3
            except (ValueError, IndexError):
                # If block is malformed (e.g., qty isn't a number), skip it.
                continue

    # Step 5: Format the structured components into the final output string.
    if not components:
        return "" # Return blank if parsing fails to produce components.

    formatted_output = []
    current_product = []

    # The first component found is the base product. Subsequent components with "CTO"
    # in their description will start a new product block.
    for comp in components:
        if not current_product or "CTO" in comp['description']:
            if current_product:
                formatted_output.append("\n".join(current_product))
                formatted_output.append("\n")
            
            # Start the new product block with the description as the title.
            current_product = [f"### {comp['description']}\n"]
        else:
            # Otherwise, add it as a component to the current product.
            current_product.append(f"• {comp['description']} (Qty: {comp['qty']})")

    # Append the last product being built.
    if current_product:
        formatted_output.append("\n".join(current_product))
        
    return "\n".join(formatted_output)


def main():
    """
    Main function to run the Streamlit application.
    """
    st.image("https://safarimicro.com/wp-content/uploads/2022/01/SafariMicro-Color-with-Solid-Icon-Copy.png", width=250)
    st.title("🚀 Safari Micro - Dell Quote Formatter")
    st.markdown("Transform your Dell Quotes into a ChannelOnline-ready format with ease!")
    
    # Added "Dell Email CTO" to the list of options
    format_type = st.radio(
        "Select Dell CTO Input Type:", 
        ["Dell Premier CTO", "TDSynnex Dell CTO", "Dell Email CTO"]
    )
    
    raw_input = st.text_area("Paste your Dell Quote data here:", height=300)
    
    if st.button("Format Output"):
        if raw_input.strip():
            # Call the appropriate function based on user selection
            if format_type == "Dell Premier CTO":
                formatted_text = format_premier_cto(raw_input)
            elif format_type == "TDSynnex Dell CTO":
                formatted_text = format_tdsynnex_cto(raw_input)
            else: # Handle the new email format
                formatted_text = format_email_cto(raw_input)
                
            st.subheader("📝 Formatted Output:")
            st.text_area("Copy and paste into ChannelOnline:", formatted_text, height=500)
            st.download_button("📥 Download Formatted Text", formatted_text, file_name="formatted_specs.txt")
        else:
            st.warning("⚠️ Please paste the Dell Quote data before formatting.")

if __name__ == "__main__":
    main()
