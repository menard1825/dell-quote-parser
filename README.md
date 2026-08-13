# Dell CTO → ChannelOnline Formatter

A small Safari Micro Streamlit utility for converting Dell CTO component exports into clean, per-system specifications that can be copied into ChannelOnline quotes.

## Supported inputs

- Dell Premier CTO
- TD SYNNEX Dell CTO
- Dell email / View in Browser CTO tables
- Generic Dell CTO text as a fallback
- Auto Detect mode for the normal workflow

## Quantity handling

Dell and distributor exports may show aggregate component quantities across the entire quote. The parser normalizes quantities to a per-system value only when the math is unambiguous.

Example: a 10-system quote with 20 memory modules is displayed as `Qty: 2`. If a component quantity does not divide evenly by the base system quantity, the original quantity is preserved and the app shows a warning instead of guessing.

## Run locally

```bash
pip install -r requirements.txt
streamlit run script.py
```

## Tests

```bash
python -m unittest discover -s tests -v
```
