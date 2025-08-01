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
    # Step 1: Clean up the input text by removing blank lines and extra whitespace.
    lines = [line.strip() for line in raw_text.strip().split('\n') if line.strip()]
    
    # Step 2: Define a regular expression to identify SKU codes.
    sku_regex = re.compile(r'^[A-Z0-9]{3}-[A-Z0-9]{4,}$')
    
    # Step 3: Filter out the table headers that might be copied from the email.
    headers = ["description", "sku", "unit price", "quantity"]
    lines = [line for line in lines if line.lower() not in headers]

    # Step 4: Process the cleaned lines to find and group components.
    components = []
    current_description_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # A component is identified by a sequence of: SKU, then '-', then a quantity.
        # Check if the current line is a SKU and if the next two lines exist and match the pattern.
        if sku_regex.match(line) and i + 2 < len(lines) and lines[i+1] == '-':
            try:
                # The line after the hyphen should be the quantity.
                qty = int(lines[i+2])
                
                # If the pattern is confirmed, group the collected description lines.
                description = " ".join(current_description_lines).strip()
                components.append({'description': description, 'sku': line, 'qty': qty})
                
                # Reset for the next component and skip the index past this component's block.
                current_description_lines = []
                i += 3 
                continue
            except ValueError:
                # This handles cases where the line after the hyphen is not a number.
                # We treat it as part of a description instead.
                pass

        # If the line is not part of a valid component block, add it to the current description.
        current_description_lines.append(line)
        i += 1

    # Step 5: Format the structured components into the final output string.
    if not components:
        return "" # Return blank if no components were successfully parsed.

    formatted_output = []
    current_product = []

    for comp in components:
        # If "CTO" is in the description, start a new product section.
        if "CTO" in comp['description']:
            if current_product:
                formatted_output.append("\n".join(current_product))
                formatted_output.append("\n")
            current_product = [f"### {comp['description']}\n"]
        else:
            # Otherwise, add the component as a bullet point to the current product.
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
