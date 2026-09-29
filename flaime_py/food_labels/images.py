from urllib.parse import quote
from urllib.parse import urlsplit
from urllib.parse import urlunsplit

from django.conf import settings


def blob_image_urls(image_path):
    """Full-size and thumbnail URLs for a store_product_images.image_path.

    The blobs mirror the on-prem image server: <prefix>/images/<path> and
    <prefix>/thumb/<path>, under AZURE_IMAGES_READ_SAS_URL, whose SAS token is
    appended to each URL.
    """
    base = urlsplit(settings.AZURE_IMAGES_READ_SAS_URL)
    root = base.path.rstrip("/")

    def url(kind):
        path = f"{root}/{kind}/{quote(image_path)}"
        return urlunsplit((base.scheme, base.netloc, path, base.query, ""))

    return {"full": url("images"), "thumb": url("thumb")}
