from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Iterable

SKU_RE = re.compile(r"\b[A-Z0-9]{3,}-[A-Z0-9]{4,}\b", re.IGNORECASE)
SOURCE_AUTO = "Auto Detect"
SOURCE_PREMIER = "Dell Premier CTO"
SOURCE_TDSYNNEX = "TDSynnex Dell CTO"
SOURCE_EMAIL = "Dell Email CTO"
SOURCE_GENERIC = "Generic CTO"

@dataclass
class Component:
    description: str
    quantity: int = 1
    category: str | None = None
    sku: str | None = None
    raw_quantity: int | None = None

    @property
    def display_description(self) -> str:
        return f"{self.category}: {self.description}" if self.category else self.description

@dataclass
class Product:
    title: str
    base_quantity: int = 1
    components: list[Component] = field(default_factory=list)

@dataclass
class ParseResult:
    source: str
    products: list[Product] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    ignored_lines: list[str] = field(default_factory=list)
    confidence: str = "medium"

    @property
    def component_count(self) -> int:
        return sum(len(p.components) for p in self.products)

    @property
    def system_count(self) -> int:
        return sum(max(p.base_quantity, 1) for p in self.products)

    @property
    def product_count(self) -> int:
        return len(self.products)

    @property
    def formatted_text(self) -> str:
        return format_result(self)

def _to_int(value: str | None, default: int = 1) -> int:
    if value is None:
        return default
    cleaned = value.strip().replace(",", "")
    return int(cleaned) if cleaned.isdigit() else default

def _last_integer(parts: Iterable[str], default: int = 1) -> int:
    for part in reversed(list(parts)):
        cleaned = part.strip().replace(",", "")
        if cleaned.isdigit():
            return int(cleaned)
    return default

def normalize_component_quantity(component_qty: int, base_qty: int) -> tuple[int, str | None]:
    component_qty = max(component_qty, 1)
    base_qty = max(base_qty, 1)
    if base_qty == 1:
        return component_qty, None
    if component_qty == base_qty:
        return 1, None
    if component_qty > base_qty and component_qty % base_qty == 0:
        return component_qty // base_qty, None
    return component_qty, (
        f"Component quantity {component_qty} does not divide evenly by base quantity "
        f"{base_qty}; kept the original quantity for review."
    )

def _append_component(product: Product, description: str, raw_qty: int, warnings: list[str], *, category: str | None = None, sku: str | None = None) -> None:
    description = description.strip().replace("Quantity:", "").strip()
    if not description:
        return
    display_qty, warning = normalize_component_quantity(raw_qty, product.base_quantity)
    if warning:
        warnings.append(f"{product.title}: {description} — {warning}")
    product.components.append(Component(description=description, quantity=display_qty, category=category.strip() if category else None, sku=sku, raw_quantity=raw_qty))

def detect_source(raw_text: str) -> tuple[str, str]:
    nonempty = [line.strip() for line in raw_text.splitlines() if line.strip()]
    if not nonempty:
        return SOURCE_GENERIC, "low"
    tab_rows = [line.split("\t") for line in nonempty if "\t" in line]
    if any(len(parts) >= 5 and parts[0].strip().lower() in {"base", "module"} for parts in tab_rows):
        return SOURCE_PREMIER, "high"
    joined_lower = "\n".join(nonempty).lower()
    if "td synnex" in joined_lower or "tdsynnex" in joined_lower:
        return SOURCE_TDSYNNEX, "high"
    has_email_header = any("description" in line.lower() and "sku" in line.lower() and "quantity" in line.lower() for line in nonempty)
    standalone_skus = sum(1 for line in nonempty if SKU_RE.fullmatch(line.strip()))
    tabular_skus = sum(1 for parts in tab_rows if any(SKU_RE.fullmatch(part.strip()) for part in parts))
    if has_email_header or standalone_skus >= 2 or tabular_skus >= 2:
        return SOURCE_EMAIL, "high" if has_email_header else "medium"
    aligned_rows = [line for line in nonempty if re.search(r"\s{2,}", line)]
    product_words = re.compile(r"\b(dell\s+pro|pro\s+max|latitude|precision|optiplex|xps|mobile\s+precision|cto)\b", re.IGNORECASE)
    if len(aligned_rows) >= 3 and any(product_words.search(line) for line in aligned_rows):
        return SOURCE_TDSYNNEX, "medium"
    return SOURCE_GENERIC, "low"

def parse_premier_cto(raw_text: str) -> ParseResult:
    result = ParseResult(source=SOURCE_PREMIER, confidence="high")
    current: Product | None = None
    for original_line in raw_text.splitlines():
        line = original_line.rstrip("\r")
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 5:
            result.ignored_lines.append(original_line)
            continue
        category, description = parts[0].strip(), parts[1].strip()
        qty = _to_int(parts[4], 1)
        if category.lower() == "base":
            title = description if description.lower().endswith("cto") else f"{description} CTO"
            current = Product(title=title, base_quantity=qty)
            result.products.append(current)
        elif category.lower() != "module" and current is not None:
            _append_component(current, description, qty, result.warnings, category=category)
        elif category.lower() != "module":
            result.ignored_lines.append(original_line)
    _validate_result(result)
    return result

_PRODUCT_FAMILY_RE = re.compile(r"\b(CTO|Mobile\s+Precision(?:\s+\d+)?|Dell\s+Pro(?:\s+(?:Base|Plus|Premium|Max))?(?:\s+\d+)?|Pro\s+Max(?:\s+\d+)?|Latitude\s+\d+|Precision\s+\d+|OptiPlex(?:\s+\w+)?|XPS\s+\d+)\b", re.IGNORECASE)

def _looks_like_tdsynnex_base(parts: list[str]) -> bool:
    if len(parts) < 3:
        return False
    searchable = " ".join(parts[:-1])
    return bool(_PRODUCT_FAMILY_RE.search(searchable)) and any(ch.isalpha() for ch in searchable)

def parse_tdsynnex_cto(raw_text: str) -> ParseResult:
    result = ParseResult(source=SOURCE_TDSYNNEX, confidence="medium")
    current: Product | None = None
    for original_line in raw_text.splitlines():
        line = original_line.strip()
        if not line:
            continue
        parts = [p.strip() for p in re.split(r"\s{2,}|\t+", line) if p.strip()]
        if len(parts) < 2:
            result.ignored_lines.append(original_line)
            continue
        if _looks_like_tdsynnex_base(parts):
            title = parts[1] if len(parts) >= 3 else parts[0]
            if not _PRODUCT_FAMILY_RE.search(title):
                title = " ".join(parts[:-1])
            current = Product(title=title.strip(), base_quantity=_last_integer(parts, 1))
            result.products.append(current)
            continue
        if current is None:
            result.ignored_lines.append(original_line)
            continue
        raw_qty = _last_integer(parts, 1)
        description_parts = parts[1:-1] if len(parts) >= 3 else parts[:-1]
        description = " ".join(description_parts).strip()
        if description:
            _append_component(current, description, raw_qty, result.warnings)
        else:
            result.ignored_lines.append(original_line)
    _validate_result(result)
    return result

def _parse_email_section(lines: list[str], result: ParseResult) -> Product | None:
    items: list[tuple[str, str | None, int]] = []
    used_lines: set[int] = set()
    for i, line in enumerate(lines):
        parts = [p.strip() for p in re.split(r"\t+", line) if p.strip()]
        sku_index = next((idx for idx, part in enumerate(parts) if SKU_RE.fullmatch(part)), None)
        if sku_index is None:
            continue
        description = " ".join(parts[:sku_index]).strip()
        if not description:
            continue
        items.append((description, parts[sku_index], _last_integer(parts[sku_index + 1:], 1)))
        used_lines.add(i)
    for i, line in enumerate(lines):
        if i in used_lines or not SKU_RE.fullmatch(line.strip()) or i == 0:
            continue
        description = lines[i - 1].strip()
        if not description or SKU_RE.fullmatch(description):
            continue
        qty = 1
        for offset in range(1, 5):
            j = i + offset
            if j >= len(lines):
                break
            candidate = lines[j].strip()
            if candidate.replace(",", "").isdigit():
                qty = _to_int(candidate)
                break
            if SKU_RE.fullmatch(candidate):
                break
            if len(candidate) > 6 and not re.fullmatch(r"[$()0-9,.*%\-\s]+", candidate) and "quantity" not in candidate.lower():
                break
        items.append((description, line.strip(), qty))
    if not items:
        return None
    base_desc, _base_sku, base_qty = items[0]
    product = Product(title=base_desc, base_quantity=base_qty)
    for description, sku, qty in items[1:]:
        _append_component(product, description, qty, result.warnings, sku=sku)
    return product

def parse_email_cto(raw_text: str) -> ParseResult:
    result = ParseResult(source=SOURCE_EMAIL, confidence="high")
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    headers = [i for i, line in enumerate(lines) if "description" in line.lower() and "sku" in line.lower() and "quantity" in line.lower()]
    sections: list[list[str]] = []
    if headers:
        for pos, index in enumerate(headers):
            end = headers[pos + 1] if pos + 1 < len(headers) else len(lines)
            sections.append(lines[index + 1:end])
    else:
        sections = [lines]
    for section in sections:
        product = _parse_email_section(section, result)
        if product:
            result.products.append(product)
    if not result.products:
        result.warnings.append("Could not detect Description/SKU/Quantity items. Try the manual input-type override or copy the full Dell component table.")
    _validate_result(result)
    return result

def parse_generic_cto(raw_text: str) -> ParseResult:
    result = ParseResult(source=SOURCE_GENERIC, confidence="low")
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    if not lines:
        _validate_result(result)
        return result
    product = _parse_email_section(lines, result)
    if product:
        result.products.append(product)
        result.confidence = "medium"
        _validate_result(result)
        return result
    product_name = lines[0]
    quantities = [int(m.group(1)) for line in lines for m in re.finditer(r"-(\d+)(?:-|$)", line)]
    product = Product(title=product_name, base_quantity=max(quantities) if quantities else 1)
    legacy_re = re.compile(r"(.+?)([A-Z0-9]{3,}-[A-Z0-9]{4,}(?:-\d+)+)$", re.IGNORECASE)
    for line in lines[1:]:
        match = legacy_re.match(line)
        if not match:
            result.ignored_lines.append(line)
            continue
        qty_match = re.search(r"-(\d+)$", match.group(2))
        _append_component(product, match.group(1).strip(), int(qty_match.group(1)) if qty_match else 1, result.warnings)
    if product.components:
        result.products.append(product)
    _validate_result(result)
    return result

def parse_quote(raw_text: str, source: str = SOURCE_AUTO) -> ParseResult:
    detected, confidence = detect_source(raw_text)
    chosen = detected if source in {SOURCE_AUTO, "Auto Detect (Recommended)"} else source
    parser = {SOURCE_PREMIER: parse_premier_cto, SOURCE_TDSYNNEX: parse_tdsynnex_cto, SOURCE_EMAIL: parse_email_cto, SOURCE_GENERIC: parse_generic_cto}.get(chosen, parse_generic_cto)
    result = parser(raw_text)
    if source in {SOURCE_AUTO, "Auto Detect (Recommended)"}:
        result.confidence = confidence
    return result

def _validate_result(result: ParseResult) -> None:
    if not result.products:
        if not result.warnings:
            result.warnings.append("No CTO products were detected in the pasted text.")
        return
    for product in result.products:
        if not product.components:
            result.warnings.append(f"{product.title}: no component lines were detected.")
        elif len(product.components) < 3:
            result.warnings.append(f"{product.title}: only {len(product.components)} component line(s) were detected; verify the pasted build is complete.")
    if result.ignored_lines and len(result.ignored_lines) > max(8, result.component_count * 2):
        result.warnings.append(f"{len(result.ignored_lines)} non-empty line(s) were not used. Review the parsing details before copying.")

def format_result(result: ParseResult) -> str:
    blocks = []
    for product in result.products:
        lines = [f"### {product.title}", ""]
        lines.extend(f"• {c.display_description} (Qty: {c.quantity})" for c in product.components)
        blocks.append("\n".join(lines).rstrip())
    return "\n\n".join(blocks)

def format_premier_cto(raw_text: str) -> str:
    return parse_premier_cto(raw_text).formatted_text

def format_tdsynnex_cto(raw_text: str) -> str:
    return parse_tdsynnex_cto(raw_text).formatted_text

def format_email_cto(raw_text: str) -> str:
    return parse_email_cto(raw_text).formatted_text

def format_generic_cto(raw_text: str) -> str:
    return parse_generic_cto(raw_text).formatted_text
