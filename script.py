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
    Formats tab-separated text copied from the 'View in Browser' 
    page of a Dell email quote. This version is designed to be more
    robust by finding and parsing distinct product sections based on
    their headers.
    """
    # Normalize line endings and remove any empty or whitespace-only lines.
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

    # Step 1: Find the start of all detailed component sections.
    # These sections are reliably marked by a header row containing "Description", "SKU", and "Quantity".
    section_starts = []
    for i, line in enumerate(lines):
        # Use 'in' for flexibility, as the exact spacing/tabs can vary.
        if "Description" in line and "SKU" in line and "Quantity" in line:
            # We add 1 because the actual data starts on the line *after* the header.
            section_starts.append(i + 1)

    # If no sections are found, the input is not in the expected format.
    # Return a helpful message to the user.
    if not section_starts:
        return "Could not find any product detail sections. Please ensure you are copying the entire quote, including the 'Description' and 'SKU' table headers."

    all_formatted_products = []
    
    # Step 2: Process each identified section individually.
    for i in range(len(section_starts)):
        start_index = section_starts[i]
        
        # The section ends where the next section begins, or at the end of the text if it's the last section.
        end_index = section_starts[i+1] -1 if i + 1 < len(section_starts) else len(lines)
        
        section_lines = lines[start_index:end_index]

        current_product_components = []
        sku_regex = re.compile(r'^[A-Z0-9]{3}-[A-Z0-9]{4,}$')

        # Step 3: Parse each line within the section.
        for line in section_lines:
            # Split the line by one or more tabs to create columns.
            parts = re.split(r'\t+', line)
            
            # A valid component line must have a SKU in the second position.
            if len(parts) >= 2 and sku_regex.match(parts[1].strip()):
                desc = parts[0].strip()
                
                # The quantity is usually in the 4th position. Default to '1' if not found.
                qty = "1"
                if len(parts) >= 4 and parts[3].strip().isdigit():
                    qty = parts[3].strip()

                # The first component found in a section is the main product title.
                if not current_product_components:
                    current_product_components.append(f"### {desc}\n")
                else:
                    # All subsequent components are formatted as list items.
                    current_product_components.append(f"• {desc} (Qty: {qty})")

        # Once a section is fully parsed, add the formatted block to our list.
        if current_product_components:
            all_formatted_products.append("\n".join(current_product_components))

    # Step 4: Join all the formatted product blocks with a double newline for spacing.
    return "\n\n".join(all_formatted_products)


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
