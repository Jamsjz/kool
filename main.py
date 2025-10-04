from typing import Literal
import mimetypes
from fastapi import (
    FastAPI,
    File,
    Form,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from svg import resize_image
from requests_toolbelt import MultipartEncoder

app = FastAPI()
from fastapi.staticfiles import StaticFiles

app.mount("/public", StaticFiles(directory="public"), name="static")


@app.get("/")
def home():
    return FileResponse("public/index.html")


@app.post("/api/image/convert")
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
