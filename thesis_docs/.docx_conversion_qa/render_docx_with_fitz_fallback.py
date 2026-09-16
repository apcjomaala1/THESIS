from __future__ import annotations

"""Run the packaged DOCX renderer with a PyMuPDF PNG fallback on Windows.

The packaged renderer remains responsible for the DOCX-to-PDF conversion,
page geometry, output naming, and command-line contract. This wrapper replaces
only pdf2image's Poppler-dependent raster function when Poppler is unavailable.
"""

import importlib.util
import sys
from pathlib import Path

import fitz


PACKAGED_RENDERER = Path(
    r"C:\Users\JM\.codex\plugins\cache\openai-primary-runtime\documents"
    r"\26.904.11930\skills\documents\render_docx.py"
)


def load_renderer():
    spec = importlib.util.spec_from_file_location(
        "codex_packaged_render_docx", PACKAGED_RENDERER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load packaged renderer: {PACKAGED_RENDERER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def convert_from_path_fitz(
    pdf_path: str,
    *,
    dpi: int,
    output_folder: str,
    **_kwargs,
) -> list[str]:
    output = Path(output_folder)
    output.mkdir(parents=True, exist_ok=True)
    document = fitz.open(pdf_path)
    scale = dpi / 72.0
    matrix = fitz.Matrix(scale, scale)
    paths: list[str] = []
    try:
        for index, page in enumerate(document, start=1):
            destination = output / f"page-fitz-{index}.png"
            page.get_pixmap(matrix=matrix, alpha=False).save(destination)
            paths.append(str(destination))
    finally:
        document.close()
    return paths


def main() -> None:
    renderer = load_renderer()
    renderer.convert_from_path = convert_from_path_fitz
    renderer.main()


if __name__ == "__main__":
    main()
