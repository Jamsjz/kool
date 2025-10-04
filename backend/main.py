import io
from typing import Annotated, Literal, Union
import mimetypes
from fastapi import (
    FastAPI,
    File,
    Form,
    HTTPException,
    Request,
    Response,
    UploadFile,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image as im
from starlette.status import HTTP_422_UNPROCESSABLE_CONTENT
from svg import resize_image, resize_svg
from requests_toolbelt import MultipartEncoder

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_methods="*",
    allow_headers="*",
)


@app.post("/")
async def root(
    scale: float = Form(...),
    image: UploadFile = File(...),
    informat: Literal["png", "svg+xml"] = Form(...),
    outformat: Literal["png", "svg+xml"] = Form(...),
):
    if (informat == "png" and outformat == "svg") or (not image.filename):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT)

    ext = mimetypes.guess_extension("image/" + outformat)
    print(ext)
    if not ext:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT)

    m = MultipartEncoder(
        fields={
            "message": "File Converted",
            "file": (
                (image.filename.removesuffix(".svg").removesuffix(".png") + ext),
                resize_image(image.file, scale, informat, outformat),
                "image/" + outformat,
            ),
        }
    )
    return Response(content=m.to_string(), media_type=m.content_type)
