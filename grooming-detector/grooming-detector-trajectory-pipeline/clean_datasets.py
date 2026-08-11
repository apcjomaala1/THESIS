"""One-shot preprocessor: rewrite source CSVs to RFC-4180 quoting.

Several source CSVs (Roblox / YouTube / Discord exports) contain unquoted
commas inside the `text` column. pandas' C engine silently column-shifts
those rows instead of raising, which produces misaligned conversation IDs
and bogus labels. This script reads each CSV with a schema-aware tolerant
parser that re-joins overflow fields back into `text`, then writes the file
back with the csv module's default quoting (RFC-4180). After this runs
once, plain `pd.read_csv` works for every dataset and the runtime loader
needs no special-casing.

Usage:
    python clean_datasets.py --in ../dataset
    python clean_datasets.py --files ../dataset/RobloxPredatorTriesToRun.csv ../dataset/anonymized_group_chat_dataset.csv
    python clean_datasets.py --in ../dataset --in-place=false   # writes <name>.clean.csv beside originals

Backups: every overwritten file is copied to `<name>.csv.bak` first.
"""

import argparse
import csv
import shutil
from pathlib import Path


_LABEL_VALS = {"0", "1", "0.0", "1.0", ""}
_IMAGE_TYPE_VALS = {"none", "screenshot", "image", "video", "gif", "sticker", ""}


def _is_valid_suffix(val, col_name):
    """Check if *val* is a plausible value for the suffix column *col_name*."""
    v = val.strip().lower()
    if col_name == "image_type":
        return v in _IMAGE_TYPE_VALS
    # label / numeric columns (is_predator, is_suspicious, …)
    return v in _LABEL_VALS


def clean_row(parts, header):
    expected = len(header)
    text_idx = header.index("text")
    prefix = parts[:text_idx]

    # suffix_cols are the columns after text
    suffix_cols = header[text_idx + 1:]
    num_suffix = len(suffix_cols)

    # Match suffix columns from the right of parts
    matched_suffix = []
    parts_idx = len(parts) - 1

    for i in range(num_suffix - 1, -1, -1):
        if parts_idx < text_idx:
            break
        val = parts[parts_idx]
        col_name = suffix_cols[i]
        if _is_valid_suffix(val, col_name):
            matched_suffix.insert(0, val.strip())
            parts_idx -= 1
        else:
            break

    # The text column absorbs all middle parts
    text_parts = parts[text_idx : parts_idx + 1]
    text_str = ",".join(text_parts)

    suffix_vals = matched_suffix
    needed = num_suffix - len(suffix_vals)
    if needed > 0:
        suffix_vals = ["0"] * needed + suffix_vals

    return prefix + [text_str] + suffix_vals


def read_repaired(path):
    """Return (header, rows) with overflow commas in `text` re-joined."""
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        if "text" not in header:
            raise ValueError(f"{path}: no `text` column — not a canonical-schema CSV")
        
        expected = len(header)
        rows = []
        for parts in reader:
            if not parts:
                continue
            if len(parts) == expected:
                rows.append(parts)          # already well-formed
            elif len(parts) > expected:
                rows.append(clean_row(parts, header))  # overflow commas in text
            # else: fewer cols than expected — skip malformed row
    return header, rows


def write_quoted(path, header, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def clean_file(path, in_place=True):
    path = Path(path)
    header, rows = read_repaired(path)
    if in_place:
        bak = path.with_suffix(path.suffix + ".bak")
        if not bak.exists():
            shutil.copy2(path, bak)
        out = path
    else:
        out = path.with_suffix(".clean.csv")
    write_quoted(out, header, rows)
    print(f"  {path.name}: {len(rows)} rows -> {out.name}")


def main():
    parser = argparse.ArgumentParser(description="Repair and re-quote canonical-schema CSVs.")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--in", dest="in_dir", help="Directory of CSVs to clean.")
    src.add_argument("--files", nargs="+", help="Specific CSV files to clean.")
    parser.add_argument("--in-place", type=lambda v: v.lower() != "false", default=True,
                        help="Overwrite source files (with .bak backup). Pass --in-place=false to write <name>.clean.csv instead.")
    args = parser.parse_args()

    if args.in_dir:
        files = sorted(Path(args.in_dir).glob("*.csv"))
        files = [p for p in files if not p.name.endswith(".bak")]
    else:
        files = [Path(p) for p in args.files]

    if not files:
        print("No CSVs found.")
        return

    print(f"Cleaning {len(files)} file(s) (in_place={args.in_place})...")
    for f in files:
        try:
            clean_file(f, in_place=args.in_place)
        except Exception as e:
            print(f"  {f.name}: SKIPPED ({e})")
    print("Done.")


if __name__ == "__main__":
    main()
