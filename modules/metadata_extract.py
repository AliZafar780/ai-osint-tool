"""
Document Metadata Extraction Module
Extracts hidden metadata from documents, images, and media files.
"""

import time
import os
import struct
from typing import Dict, List, Optional
from datetime import datetime
from .base import OSINTModule, ModuleResult


class MetadataExtract(OSINTModule):
    """Document metadata extraction - EXIF, document properties, hidden data."""

    name = "metadata_extract"
    description = "Document metadata extraction - EXIF, document properties, file signatures"

    # Supported file signatures (magic bytes)
    FILE_SIGNATURES = {
        b"\xff\xd8\xff": "JPEG Image",
        b"\x89PNG\r\n\x1a\n": "PNG Image",
        b"GIF8": "GIF Image",
        b"BM": "BMP Image",
        b"%PDF": "PDF Document",
        b"PK\x03\x04": "ZIP/DOCX/XLSX/PPTX Archive",
        b"\x1f\x8b\x08": "GZIP Archive",
        b"Rar!\x1a\x07": "RAR Archive",
        b"\x49\x44\x33": "MP3 Audio (ID3)",
        b"\xff\xfb": "MP3 Audio",
        b"RIFF": "AVI/WAV File",
    }

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)

    def _detect_file_type(self, filepath: str) -> Dict:
        """Detect file type from magic bytes."""
        result = {
            "filename": os.path.basename(filepath),
            "extension": os.path.splitext(filepath)[1].lower(),
            "size_bytes": 0,
            "file_type": "Unknown",
            "confidence": "low",
        }

        try:
            result["size_bytes"] = os.path.getsize(filepath)
            with open(filepath, "rb") as f:
                magic = f.read(16)

            for sig, ftype in self.FILE_SIGNATURES.items():
                if magic.startswith(sig):
                    result["file_type"] = ftype
                    result["confidence"] = "high"
                    break
        except OSError as e:
            result["error"] = str(e)[:100]

        return result

    def _extract_pdf_metadata(self, filepath: str) -> Dict:
        """Extract metadata from PDF files."""
        metadata = {}
        try:
            with open(filepath, "rb", errors="replace") as f:
                content = f.read(100000)  # Read first 100KB

            # Extract info dictionary
            text = content.decode("latin-1", errors="replace")

            # Look for common PDF metadata fields
            fields = {
                "/Title": "title",
                "/Author": "author",
                "/Subject": "subject",
                "/Keywords": "keywords",
                "/Creator": "creator",
                "/Producer": "producer",
                "/CreationDate": "creation_date",
                "/ModDate": "modification_date",
            }

            for pdf_field, our_field in fields.items():
                if pdf_field in text:
                    start = text.index(pdf_field) + len(pdf_field)
                    # Extract text between parentheses or following
                    remaining = text[start:].strip()
                    if remaining.startswith("("):
                        end = remaining.index(")") if ")" in remaining else -1
                        if end > 0:
                            metadata[our_field] = remaining[1:end]
                    else:
                        # Try to get next word
                        parts = remaining.split("/")
                        if parts:
                            metadata[our_field] = parts[0].strip()[:100]

            # Extract pages count
            page_count = text.count("/Type /Page")
            if page_count > 0:
                metadata["page_count"] = page_count

        except Exception as e:
            metadata["error"] = str(e)[:100]

        return metadata

    def _extract_image_metadata(self, filepath: str) -> Dict:
        """Extract metadata from image files using PIL if available."""
        metadata = {}
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS, GPSTAGS

            img = Image.open(filepath)
            metadata["format"] = img.format
            metadata["mode"] = img.mode
            metadata["width"] = img.width
            metadata["height"] = img.height

            exif = img._getexif()
            if exif:
                for tag_id, value in exif.items():
                    tag_name = TAGS.get(tag_id, tag_id)
                    if isinstance(value, bytes):
                        try:
                            value = value.decode("utf-8", errors="replace")
                        except Exception:
                            value = str(value)
                    metadata[str(tag_name)] = str(value)[:200]

        except ImportError:
            metadata["note"] = "Install Pillow for EXIF extraction"
        except Exception as e:
            metadata["error"] = str(e)[:100]

        return metadata

    def _extract_docx_metadata(self, filepath: str) -> Dict:
        """Extract metadata from Office Open XML files (docx/xlsx/pptx)."""
        metadata = {}
        try:
            import zipfile
            import xml.etree.ElementTree as ET

            with zipfile.ZipFile(filepath) as z:
                # Read core properties
                if "docProps/core.xml" in z.namelist():
                    core_xml = z.read("docProps/core.xml")
                    root = ET.fromstring(core_xml)
                    ns = {
                        "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
                        "dc": "http://purl.org/dc/elements/1.1/",
                        "dcterms": "http://purl.org/dc/terms/",
                    }

                    for elem in root.iter():
                        tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
                        if elem.text and elem.text.strip():
                            metadata[tag] = elem.text.strip()[:200]

                # Read app properties
                if "docProps/app.xml" in z.namelist():
                    app_xml = z.read("docProps/app.xml")
                    root = ET.fromstring(app_xml)
                    for elem in root.iter():
                        tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
                        if elem.text and elem.text.strip():
                            metadata[f"app_{tag}"] = elem.text.strip()[:200]

        except ImportError:
            metadata["note"] = "zipfile available (stdlib)"
        except Exception as e:
            metadata["error"] = str(e)[:100]

        return metadata

    def execute(self, target: str, **kwargs) -> ModuleResult:
        """
        Extract metadata from a file.
        Target can be a local file path or URL to download.
        """
        start = time.time()

        results = {
            "target": target,
            "file_info": {},
            "metadata": {},
            "extraction_methods_used": [],
        }

        filepath = target

        # If target is a URL, download it first
        if target.startswith(("http://", "https://")):
            try:
                import requests
                resp = requests.get(target, timeout=15, stream=True)
                if resp.status_code == 200:
                    temp_dir = os.path.join(
                        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        ".cache",
                    )
                    os.makedirs(temp_dir, exist_ok=True)
                    local_path = os.path.join(temp_dir, "downloaded_temp_file")
                    with open(local_path, "wb") as f:
                        f.write(resp.content)
                    filepath = local_path
                    results["download_info"] = {
                        "url": target,
                        "size_bytes": len(resp.content),
                        "content_type": resp.headers.get("Content-Type", ""),
                    }
                    results["extraction_methods_used"].append("url_download")
            except Exception as e:
                return self._failed(f"Cannot download URL: {e}")

        # Detect file type
        results["file_info"] = self._detect_file_type(filepath)
        ext = results["file_info"]["extension"]
        ftype = results["file_info"]["file_type"]

        # Choose extraction method based on file type
        if "PDF" in ftype:
            results["metadata"] = self._extract_pdf_metadata(filepath)
            results["extraction_methods_used"].append("pdf_parser")
        elif ext in (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"):
            results["metadata"] = self._extract_image_metadata(filepath)
            results["extraction_methods_used"].append("pil_exif")
        elif ext in (".docx", ".xlsx", ".pptx"):
            results["metadata"] = self._extract_docx_metadata(filepath)
            results["extraction_methods_used"].append("ooxml_parser")
        else:
            # Try all methods
            results["metadata"]["note"] = f"Unsupported format: {ftype}"
            results["extraction_methods_used"].append("unsupported_format")

        # Clean up downloaded file
        if target.startswith(("http://", "https://")) and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except OSError:
                pass

        duration = (time.time() - start) * 1000
        return self._success(results, duration)
