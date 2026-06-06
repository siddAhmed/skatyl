#!/usr/bin/env python3
"""
QMK Keymap Layer Formatter
===========================
Reads keymap.c and reformats each LAYOUT(...) block so that keycodes
are vertically aligned column-by-column, row-by-row, with a visual
split between the left and right keyboard halves.

Usage:
    python format_layers.py                    # dry-run, prints to stdout
    python format_layers.py --inplace          # overwrites keymap.c in place
    python format_layers.py -o output.c        # writes to a specific file

The script:
  1. Finds every `[N] = LAYOUT(` ... `)` block.
  2. Strips out comment lines (//---) and blank lines inside the block.
  3. Splits the remaining keycodes by top-level commas (respecting parens).
  4. Groups them into rows: 3 main rows of 5+5 and 1 thumb row of 3+3.
  5. Pads each column to the width of the widest keycode in that column
     across ALL layers and ALL rows.
  6. Re-emits each layer with:
     - Columns aligned vertically
     - A visual gap between left and right halves
     - Split separator comment lines matching the row width
     - Thumb keys centered toward the split (under cols 2-4 / 5-7)
"""

import re
import sys
import argparse
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────
KEYS_PER_ROW = [10, 10, 10, 6]   # 3 main rows of 10 + thumb row of 6
LEFT_KEYS = 5                     # columns per half (main rows)
RIGHT_KEYS = 5
THUMB_LEFT = 3                    # thumb keys per half
THUMB_RIGHT = 3
HALF_GAP = "        "             # 8-space gap between halves
INDENT = "      "                 # 6 spaces for main key rows
SEP_PREFIX = "  //"               # prefix for separator comments


def find_layout_blocks(text: str):
    """
    Yield (start, end, layer_num, raw_content) for each LAYOUT block.
    """
    pattern = re.compile(
        r'(\[(\d+)\]\s*=\s*LAYOUT\s*\()'
        r'(.*?)'
        r'(\n\s*\))',
        re.DOTALL,
    )
    for m in pattern.finditer(text):
        yield m.start(), m.end(), int(m.group(2)), m.group(3)


def extract_keycodes(raw_content: str) -> list[str]:
    """
    Extract keycodes from raw LAYOUT content, splitting on top-level
    commas only (respecting parenthesis nesting).
    """
    lines = raw_content.split('\n')
    code_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('//'):
            continue
        code_lines.append(stripped)

    joined = ' '.join(code_lines).strip().rstrip(',')

    keycodes = []
    depth = 0
    current = []
    for ch in joined:
        if ch == '(':
            depth += 1
            current.append(ch)
        elif ch == ')':
            depth -= 1
            current.append(ch)
        elif ch == ',' and depth == 0:
            token = ''.join(current).strip()
            if token:
                keycodes.append(token)
            current = []
        else:
            current.append(ch)
    token = ''.join(current).strip()
    if token:
        keycodes.append(token)

    return keycodes


def keycodes_to_rows(keycodes: list[str]) -> list[list[str]]:
    """Split flat keycode list into rows based on KEYS_PER_ROW."""
    rows = []
    idx = 0
    for size in KEYS_PER_ROW:
        rows.append(keycodes[idx:idx + size])
        idx += size
    return rows


# Mapping: thumb key index → main column index it sits under
THUMB_TO_COL = [2, 3, 4, 5, 6, 7]  # left thumbs under cols 2-4, right under 5-7


def compute_column_widths(all_layers_rows):
    """
    Compute per-column max widths across all layers.
    Thumb keys share column widths with the main row columns they
    physically sit under (left thumbs → cols 2-4, right → cols 5-7).
    Returns main_col_widths[10].
    """
    main_widths = [0] * (LEFT_KEYS + RIGHT_KEYS)

    for rows in all_layers_rows:
        # Main rows (0-2): 10 keys each
        for row_i in range(3):
            if row_i < len(rows):
                for col_j, kc in enumerate(rows[row_i]):
                    main_widths[col_j] = max(main_widths[col_j], len(kc))
        # Thumb row (3): fold into the main column they sit under
        if len(rows) > 3:
            for thumb_j, kc in enumerate(rows[3]):
                col = THUMB_TO_COL[thumb_j]
                main_widths[col] = max(main_widths[col], len(kc))

    return main_widths


def compute_layout_geometry(main_widths):
    """
    Compute character positions for the split layout.
    Returns (left_half_width, right_half_width, col2_start_pos).
    """
    # Left half: INDENT + 5 padded keys joined by ",  " + trailing ","
    left_w = len(INDENT)
    for i in range(LEFT_KEYS):
        left_w += main_widths[i]
        if i < LEFT_KEYS - 1:
            left_w += 3   # ",  "
    left_w += 1  # trailing "," after column 4

    # Right half: 5 padded keys joined by ",  " + trailing ","
    right_w = 0
    for i in range(RIGHT_KEYS):
        right_w += main_widths[LEFT_KEYS + i]
        if i < RIGHT_KEYS - 1:
            right_w += 3
    right_w += 1  # trailing ","

    # Column 2 start position (where left thumb keys begin)
    col2_pos = len(INDENT)
    for i in range(2):
        col2_pos += main_widths[i] + 3  # width + ",  "

    return left_w, right_w, col2_pos


def make_split_separator(left_half_width, right_half_width):
    """Build a split separator: //---left---        ---right---"""
    left_dashes = left_half_width - len(SEP_PREFIX)
    return SEP_PREFIX + '-' * left_dashes + HALF_GAP + '-' * right_half_width


def format_layer(
    layer_num, rows, main_widths,
    is_last_layer, separator, left_half_width, col2_pos,
):
    """Format a single layer into aligned, split rows."""
    right_start = left_half_width + len(HALF_GAP)

    lines = []
    lines.append(f"  [{layer_num}] = LAYOUT(")
    lines.append("")

    for row_i, row_keys in enumerate(rows):
        is_thumb = (row_i == len(rows) - 1)

        if is_thumb:
            # ── Thumb row: 3 left + 3 right, aligned under cols 2-4 / 5-7 ──
            left = row_keys[:THUMB_LEFT]
            right = row_keys[THUMB_LEFT:]

            # Pad each thumb key to the main column width it sits under
            left_parts = [kc.ljust(main_widths[THUMB_TO_COL[i]])
                          for i, kc in enumerate(left)]
            left_str = ",  ".join(left_parts) + ","

            # Right thumb keys (no trailing comma — last keys in LAYOUT)
            right_parts = [kc.ljust(main_widths[THUMB_TO_COL[THUMB_LEFT + i]])
                           for i, kc in enumerate(right)]
            right_str = ",  ".join(right_parts).rstrip()

            # Position: left thumbs start at col2 position
            thumb_prefix = " " * col2_pos
            left_with_prefix = thumb_prefix + left_str

            # Right thumbs start at right_start
            padding = right_start - len(left_with_prefix)
            row_line = left_with_prefix + " " * max(padding, 2) + right_str

        else:
            # ── Main row: 5 left + 5 right ──
            left = row_keys[:LEFT_KEYS]
            right = row_keys[LEFT_KEYS:]

            left_parts = [kc.ljust(main_widths[i]) for i, kc in enumerate(left)]
            left_str = INDENT + ",  ".join(left_parts) + ","

            right_parts = [kc.ljust(main_widths[LEFT_KEYS + i])
                           for i, kc in enumerate(right)]
            right_str = ",  ".join(right_parts).rstrip() + ","

            row_line = left_str + HALF_GAP + right_str

        lines.append(separator)
        lines.append(row_line)

    lines.append(separator)
    lines.append("")

    if is_last_layer:
        lines.append("  )")
    else:
        lines.append("  ),")

    return '\n'.join(lines)


def format_keymap(input_path: str) -> str:
    """Read the keymap file, reformat all LAYOUT blocks, return the new text."""
    text = Path(input_path).read_text(encoding='utf-8')

    # First pass: extract all layers
    blocks = list(find_layout_blocks(text))
    all_rows = []
    for start, end, layer_num, raw in blocks:
        kcs = extract_keycodes(raw)
        expected = sum(KEYS_PER_ROW)
        if len(kcs) != expected:
            print(
                f"WARNING: Layer {layer_num} has {len(kcs)} keycodes, "
                f"expected {expected}.",
                file=sys.stderr,
            )
        all_rows.append(keycodes_to_rows(kcs))

    # Compute global geometry
    main_widths = compute_column_widths(all_rows)
    left_w, right_w, col2_pos = compute_layout_geometry(main_widths)
    separator = make_split_separator(left_w, right_w)

    # Second pass: replace each block in reverse order
    result = text
    for i in range(len(blocks) - 1, -1, -1):
        start, end, layer_num, raw = blocks[i]
        is_last = (i == len(blocks) - 1)

        formatted = format_layer(
            layer_num, all_rows[i], main_widths,
            is_last, separator, left_w, col2_pos,
        )

        after = result[end:]
        consumed = 0
        if after.startswith(','):
            consumed = 1

        result = result[:start] + formatted + '\n' + result[end + consumed:]

    return result


def main():
    parser = argparse.ArgumentParser(description="Format QMK keymap layers")
    parser.add_argument(
        'input', nargs='?', default='keymap.c',
        help='Input keymap.c file (default: keymap.c)',
    )
    parser.add_argument(
        '--inplace', '-i', action='store_true',
        help='Modify the file in place',
    )
    parser.add_argument(
        '--output', '-o', default=None,
        help='Write output to this file instead of stdout',
    )
    args = parser.parse_args()

    result = format_keymap(args.input)

    if args.inplace:
        Path(args.input).write_text(result, encoding='utf-8')
        print(f"✓ Formatted {args.input} in place.", file=sys.stderr)
    elif args.output:
        Path(args.output).write_text(result, encoding='utf-8')
        print(f"✓ Wrote formatted output to {args.output}.", file=sys.stderr)
    else:
        print(result)


if __name__ == '__main__':
    main()
