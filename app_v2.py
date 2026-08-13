import streamlit as st

from parser import SOURCE_EMAIL, SOURCE_GENERIC, SOURCE_PREMIER, SOURCE_TDSYNNEX, parse_quote

SOURCE_OPTIONS = ["Auto Detect (Recommended)", SOURCE_PREMIER, SOURCE_TDSYNNEX, SOURCE_EMAIL, SOURCE_GENERIC]


def clear_quote():
    st.session_state.raw_input = ""
    st.session_state.pop("parse_result", None)


def main():
    st.set_page_config(page_title="Safari Micro | Dell CTO Formatter", page_icon="🖥️", layout="wide")
    st.image("https://safarimicro.com/wp-content/uploads/2022/01/SafariMicro-Color-with-Solid-Icon-Copy.png", width=230)
    st.title("Dell CTO → ChannelOnline")
    st.caption("Paste a Dell CTO build, verify what was detected, then copy the cleaned per-system specifications into ChannelOnline.")

    st.subheader("1. Paste the Dell build")
    source = st.selectbox("Input type", SOURCE_OPTIONS, help="Auto Detect is recommended. Use a manual override if the detected source looks wrong.")
    st.text_area("Dell quote data", key="raw_input", height=320, placeholder="Paste the Dell Premier, TD SYNNEX, or Dell email CTO component data here...")

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
        st.info("Auto Detect will identify the most likely Dell source, but you can override it at any time.")
        return

    st.divider()
    st.subheader("2. Verify the build")
    icon = {"high": "🟢", "medium": "🟡", "low": "🟠"}.get(result.confidence, "⚪")
    st.write(f"{icon} **Detected input:** {result.source} · **{result.confidence.title()} confidence**")

    a, b, c = st.columns(3)
    a.metric("Configurations", result.product_count)
    b.metric("Systems in quote", result.system_count)
    c.metric("Components detected", result.component_count)

    if result.warnings:
        st.warning(f"Review {len(result.warnings)} parsing warning(s) before copying.")
        with st.expander("Parsing warnings", expanded=True):
            for warning in result.warnings:
                st.write(f"• {warning}")
    else:
        st.success("The build parsed cleanly. Quantities below are normalized per system when the quote math is unambiguous.")

    with st.expander("Parsing details"):
        st.write(f"**Ignored non-empty lines:** {len(result.ignored_lines)}")
        if result.ignored_lines:
            st.code("\n".join(result.ignored_lines[:25]), language=None, wrap_lines=True)

    st.subheader("3. Copy into ChannelOnline")
    if result.formatted_text:
        st.caption("Use the copy control on the output box, then paste directly into ChannelOnline.")
        st.code(result.formatted_text, language=None, wrap_lines=True, height=500)
        st.download_button("Download TXT", result.formatted_text, file_name="dell_cto_channelonline.txt", mime="text/plain")
    else:
        st.error("No ChannelOnline output was produced. Check the warnings above and try a manual input type.")


if __name__ == "__main__":
    main()
