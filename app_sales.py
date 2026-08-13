import re

import streamlit as st

from parser import SOURCE_EMAIL, SOURCE_GENERIC, SOURCE_PREMIER, SOURCE_TDSYNNEX, parse_quote

SOURCE_OPTIONS = ["Auto Detect (Recommended)", SOURCE_PREMIER, SOURCE_TDSYNNEX, SOURCE_EMAIL, SOURCE_GENERIC]


def clear_quote():
    st.session_state.raw_input = ""
    st.session_state.pop("parse_result", None)


def friendly_warning(warning: str) -> str:
    if "does not divide evenly by base quantity" in warning:
        description = warning.split(" — ", 1)[0] if " — " in warning else "A component"
        return f"{description} has an unusual quantity. Double-check that line before copying."
    if "Could not detect Description/SKU/Quantity" in warning:
        return "I couldn't confidently read the Dell component table. Try copying the full build or choose the input type manually."
    if "No CTO products were detected" in warning:
        return "I couldn't find a Dell CTO build in the pasted text. Try copying the full build again."
    if "no component lines were detected" in warning:
        product = warning.split(":", 1)[0]
        return f"I found {product}, but not its components. Make sure the full build was copied."
    if re.search(r"only \d+ component line\(s\) were detected", warning):
        return "Only a few components were found. Make sure the entire Dell build was copied before using the output."
    if "non-empty line(s) were not used" in warning:
        return "Some pasted information wasn't used. Give the output a quick look before copying."
    return warning


def main():
    st.set_page_config(page_title="Safari Micro | Dell CTO Formatter", page_icon="🖥️", layout="wide")
    st.image("https://safarimicro.com/wp-content/uploads/2022/01/SafariMicro-Color-with-Solid-Icon-Copy.png", width=230)
    st.title("Dell CTO → ChannelOnline")
    st.caption("Paste a Dell CTO build and turn it into clean, ChannelOnline-ready specs.")

    st.subheader("1. Paste the Dell build")
    st.text_area(
        "Dell quote data",
        key="raw_input",
        height=320,
        placeholder="Paste the Dell Premier, TD SYNNEX, or Dell email CTO build here...",
    )

    with st.expander("Input options"):
        source = st.selectbox(
            "Input type",
            SOURCE_OPTIONS,
            help="Auto Detect is recommended. Only change this if the build doesn't format correctly.",
        )

    left, middle, _ = st.columns([1.4, 1, 5])
    with left:
        process = st.button("Format for ChannelOnline", type="primary", use_container_width=True)
    with middle:
        st.button("Clear", on_click=clear_quote, use_container_width=True)

    if process:
        raw = st.session_state.get("raw_input", "")
        if raw.strip():
            st.session_state.parse_result = parse_quote(raw, source)
        else:
            st.warning("Paste a Dell CTO build before formatting.")

    result = st.session_state.get("parse_result")
    if result is None:
        return

    st.divider()

    if result.warnings:
        st.warning("⚠️ Please review this build before copying.")
        with st.expander("What needs attention", expanded=True):
            for warning in result.warnings:
                st.write(f"• {friendly_warning(warning)}")
    else:
        st.success("✅ Build looks good — ready to copy into ChannelOnline.")

    st.subheader("2. Copy into ChannelOnline")
    if result.formatted_text:
        st.caption("Use the copy button on the output box, then paste directly into your ChannelOnline quote.")
        st.code(result.formatted_text, language=None, wrap_lines=True, height=500)
        st.download_button("Download TXT", result.formatted_text, file_name="dell_cto_channelonline.txt", mime="text/plain")
    else:
        st.error("No ChannelOnline output was produced. Try copying the full Dell build again or change the input type under Input options.")

    with st.expander("Show details"):
        st.write(f"**Detected input:** {result.source} ({result.confidence.title()} confidence)")
        a, b, c = st.columns(3)
        a.metric("Configurations", result.product_count)
        b.metric("Systems", result.system_count)
        c.metric("Components", result.component_count)

        if result.warnings:
            st.markdown("**Technical warnings**")
            for warning in result.warnings:
                st.write(f"• {warning}")

        if result.ignored_lines:
            st.markdown(f"**Unused pasted lines:** {len(result.ignored_lines)}")
            st.code("\n".join(result.ignored_lines[:25]), language=None, wrap_lines=True)


if __name__ == "__main__":
    main()
