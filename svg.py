from typing import BinaryIO, Literal
from fastapi import HTTPException, status
from lxml import etree
import nocairosvg as cairosvg
import io
import re
from PIL import Image as im


def parse_dimension(value: str) -> float | None:
    """Convert '100px' or '10cm' to a float. Returns None if not numeric."""
    if not value:
        return None
    match = re.match(r"([0-9.]+)", value)
    return float(match.group(1)) if match else None


def resize_image(
    image: BinaryIO,
    scale: float,
    informat: Literal["svg+xml", "png"] = "svg+xml",
    outformat: Literal["svg+xml", "png"] = "png",
) -> bytes:
    if informat == "svg+xml":
        return resize_svg(image.read().decode(), scale, outformat)
    return resize_png(image.read(), scale)


def resize_png(imagebytes: bytes, scale: float) -> bytes:
    image = im.open(io.BytesIO(imagebytes))
    image = image.resize(
        size=(int(image.width * scale), int(image.height * scale)),
    )
    buf = io.BytesIO()
    image.save(buf, "PNG")
    return buf.getvalue()


def resize_svg(
    svg_str: str,
    scale: float,
    outformat: Literal["png", "svg+xml"] = "png",
) -> bytes:
    """
    Convert an SVG string to PNG bytes, scaling output while preserving contents.
    """
    # Parse SVG once just to know original size
    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.fromstring(svg_str.encode("utf-8"), parser)

    orig_width = parse_dimension(root.get("width"))
    orig_height = parse_dimension(root.get("height"))

    # Fallback: extract from viewBox if width/height missing
    if (not orig_width or not orig_height) and "viewBox" in root.attrib:
        _, _, vw, vh = map(float, root.attrib["viewBox"].split())
        orig_width, orig_height = vw, vh

    if not orig_width or not orig_height:
        raise ValueError("SVG must have width/height or viewBox for scaling.")

    imagebytes = (cairosvg.svg2png if outformat == "png" else cairosvg.svg2svg)(
        bytestring=svg_str.encode("utf-8"),
        output_width=orig_width * scale,
        output_height=orig_height * scale,
    )
    if not imagebytes:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT)

    return imagebytes


if __name__ == "__main__":
    from PIL import Image as im

    with open("image.png", "rb") as file:
        out_bytes = resize_png(file.read(), scale=3)
        image = im.open(io.BytesIO(out_bytes))
        image.save("image.png")
