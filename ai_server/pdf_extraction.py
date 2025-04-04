import os
import pymupdf
import re

dimlimit = 100  # 100  # each image side must be greater than this
relsize = 0  # 0.05  # image : image size ratio must be larger than this (5%)
abssize = 2048  # 2048  # absolute image size limit 2 KB: ignore if smaller
imgdir = "./data/extracted_images/"  # found images are stored in this subfolder

def extract_text(doc: pymupdf.Document, max_length=300) -> list[str]:
    chunks = []
    all_text = chr(12).join([page.get_text() for page in doc])
    sentences = re.split(r'\n', all_text)  # Split on empty lines (paragraphs)
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_length:
            current_chunk += sentence + "\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + "\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def extract_images(doc: pymupdf.Document) -> Exception | None:
    global dimlimit, relsize, abssize, imgdir

    if not os.path.exists(imgdir):  # make subfolder if necessary
        os.mkdir(imgdir)

    page_count = doc.page_count  # number of pages

    xreflist = []
    imglist = []
    try:
        for pno in range(page_count):
            il = doc.get_page_images(pno)
            imglist.extend([x[0] for x in il])
            for img in il:
                xref = img[0]
                if xref in xreflist:
                    continue
                width = img[2]
                height = img[3]
                if min(width, height) <= dimlimit:
                    continue
                image = recoverpix(doc, img)
                n = image["colorspace"]
                imgdata = image["image"]

                if len(imgdata) <= abssize:
                    continue
                if len(imgdata) / (width * height * n) <= relsize:
                    continue

                imgfile = os.path.join(imgdir, "img%05i.%s" % (xref, image["ext"]))
                fout = open(imgfile, "wb")
                fout.write(imgdata)
                fout.close()
                xreflist.append(xref)
    except Exception as e:
        return e

def recoverpix(doc, item):
    xref = item[0]  # xref of PDF image
    smask = item[1]  # xref of its /SMask

    # special case: /SMask or /Mask exists
    if smask > 0:
        pix0 = pymupdf.Pixmap(doc.extract_image(xref)["image"])
        if pix0.alpha:  # catch irregular situation
            pix0 = pymupdf.Pixmap(pix0, 0)  # remove alpha channel
        mask = pymupdf.Pixmap(doc.extract_image(smask)["image"])

        try:
            pix = pymupdf.Pixmap(pix0, mask)
        except Exception as _:  # fallback to original base image in case of problems
            pix = pymupdf.Pixmap(doc.extract_image(xref)["image"])

        if pix0.n > 3:
            ext = "pam"
        else:
            ext = "png"

        return {  # create dictionary expected by caller
                "ext": ext,
                "colorspace": pix.colorspace.n,
                "image": pix.tobytes(ext),
                }

    # special case: /ColorSpace definition exists
    # to be sure, we convert these cases to RGB PNG images
    if "/ColorSpace" in doc.xref_object(xref, compressed=True):
        pix = pymupdf.Pixmap(doc, xref)
        pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
        return {  # create dictionary expected by caller
                "ext": "png",
                "colorspace": 3,
                "image": pix.tobytes("png"),
                }
    return doc.extract_image(xref)
