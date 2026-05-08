---
created: 2026-05-02
---
## How servers handle file uploads

could you please improve this section for my article? mostly fixing English, paraphrasing, but you can make it a bit more concise - but only if you preserve all explanations and information. it is a technical, non-fluff article.
### Multi-part requests

- Most commonly, files are uploaded via **multi-part HTTP requests**.

A typical file upload process works as follows:

1. **Frontend: HTML form and user interaction**
	- Users upload files through HTML forms containing an `<input type="file">` element.
	- The `action` attribute defines the server endpoint that receives the upload request.
	- The `enctype` attribute defines how form data is encoded before transmission:
		- Multi-part file uploads use `multipart/form-data` (`enctype="multipart/form-data"`). The browser encodes form data as a MIME message split into separate parts for each form field using a boundary string.
		- The default encoding is `application/x-www-form-urlencoded`, but it can't handle binary files.

>[!example]
> ```HTML
> <form action="/upload" method="post" enctype="multipart/form-data">
>   <input type="file" name="file_to_upload" id="file_to_upload">
>   <input type="submit" value="Upload" name="submit">
> </form>
> ```

2. **Client-side validation (Optional)**
	- Applications may implement client-side validation using JavaScript to inspect file properties before submission, such as file name, extension, size, and MIME type.
	- However, **client-side validation can serve only for user convenience and never as a security control**. 
	- Everything on the client-side is client-controlled; such restrictions can be bypassed, for example, using a web proxy (such as Burp Suite) or via direct file uploads using `curl`. 
	- See [[File upload#Bypassing client-side controls]].

3. **Transmission: HTTP request structure**
	- Submitting the form triggers a `POST` request to the server.
	- The `Content-Type` header is set to `multipart/form-data`, matching the form’s `enctype`.
	- The request body is split into multiple parts using a boundary string.
	- Each part represents a field or file and includes its own headers:
		- `Content-Disposition`: Defines the field name and original filename.
		- `Content-Type`: Defines the MIME of the file content.
	
>[!example]+
> ```HTTP
> POST /upload HTTP/1.1
> Host: example.com
> <other headers...>
> Content-Length: <total size of the request body>
> Content-Type: multipart/form-data; boundary=---------------------------7970204168003706453399115153
> 
> ---------------------------7970204168003706453399115153
> Content-Disposition: form-data; name="file"; filename="mountains.jpg"
> Content-Type: image/jpeg
> 
> <binary content of the JPEG file...>
> ---------------------------7970204168003706453399115153
> Content-Disposition: form-data; name="description"
> 
> A very interesting description of an image.
> 
> -----------------------------7970204168003706453399115153
> <other form fields...>
> ```

4. **Backend handling**
	- The server parses the multipart request to extract uploaded files and other form fields.
	- Common implementations include: `multer` (Node.js), `Werkzeug` (Flask, Python), `$_FILES` (PHP), Django's built-in file handling (Python), etc.
	- Uploaded files are typically stored temporarily in directories like `/tmp` or `/var/tmp` before further processing.

5. **Validation**
	- The backend may validate uploaded files, including:
	    - File extension (e.g., `.jpg`, `.png`)
	    - MIME type (`Content-Type` header)
	    - File size
	    - File signature (magic bytes; they identify the actual file type regardless of extension of MIME type)
	    - File content
	- **Weak or incomplete validation is one of the most common causes of file upload vulnerabilities.**

6. **Server-side processing**
	- After validation, uploaded files may be processed using external libraries or system utilities, such as:
		- **Image processing:** resizing, thumbnail generation, watermarking, format conversion (e.g., `ImageMagick`, `GD`, `Pillow`, `GraphicsMagick`, etc).
		- **Document processing:** PDF/Office parsing, preview generation, format conversion.
		- **Archive extraction:** ZIP, TAR, RAR, 7z, etc.
		- **Metadata extraction:** EXIF readers, ID3 parsers, and similar tools
	- These libraries can also be used as an attack vector. Notable examples include `ImageTragick` (`ImageMagick` RCE), `Ghostscript` command injection, and Zip Slip (path traversal during archive extraction).

7. **Storage**
	- After processing, files are stored depending on application design:
		- Local filesystem directories
		- Databases (database BLOB fields)
		- Cloud storage (e.g., AWS S3, Azure Blob Storage, Google Cloud Storage, etc.)
		- Network filesystems (e.g., NFS, SMB/CIFS shares, etc.)
	- In many implementations, filenames are hashed or randomized to prevent enumeration.

8. **Retrieval and access**
	- Uploaded files are often served directly to users, sometimes from within the webroot.
	- If an uploaded file has an executable extension (e.g., `.php`, `.jsp`, `.asp`, `.py`), resides in a web-accessible directory, and the server is configured to execute files with that extension, then **accessing the file URL will execute the file rather than serve it as static content**. This is the basis of **RCE via file upload**.
	- If the file extension is executable but the server is **not configured to execute it**, the server typically returns an error or serves the file as plain text (in some cases, this may expose source code or sensitive data).

>[!important] Accessing executable files in a web-accessible directory may result in server-side execution of the uploaded code. 

>[!note] If execution is not configured for a given extension, the file is usually served as static content or rejected with an error. In some cases, raw file contents may still be exposed, potentially leaking sensitive information or source code.

### Raw binary upload

- Instead of wrapping the file in a form, it can be sent **directly** as the request body, using HTTP `PUT` or `POST` methods. 
- `Content-Type` is set to `application/octet-stream`, `image/png`, etc.
- The body is raw file bytes.

```HTTP
PUT /upload/file.png
Content-Type: image/png

<binary data>
```

- This is commonly used in REST APIs, simple direct uploads, uploading to pre-defined file URLs.

### Chunked / streamed uploads (HTTP streaming)

- The file is sent **as a stream** instead of a single payload. 
- This type of upload uses **HTTP chunked transfer encoding** (`Transfer-Encoding: chunked`), or a custom chunk protocol (client splits file manually).

```HTTP
Transfer-Encoding: chunked
```

- This is used for very large file to avoid memory limits.

### Resumable upload protocols

- Instead of a single request, the file is uploaded in parts with session tracking. A common example is the **`tus` protocol**.
- It provides features like pause/resume, retry failed chunks, track upload offsets, etc.

>**[`tus`](https://tus.io/)** is an open, resumable file upload protocol designed to make uploading large or interrupted files reliable and efficient across different platforms and languages. It defines a simple, standardized HTTP-based mechanism for resuming interrupted uploads without restarting from the beginning.


### Base64 or binary-in-JSON

- The file is Base64-encoded and embedded in a JSON payload.

```JSON
{
  "filename": "image.png",
  "data": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

- Cons are ~33% size overhead, CPU cost for encoding/decoding.

### WebSocket streaming uploads

- File data is sent over an open WebSocket connection.


### Direct object storage uploads (pre-signed URLs)

Instead of uploading through your server:

- Client uploads directly to storage (S3, GCS, etc.)
- Server provides temporary signed URL

**Flow:**

1. Backend generates signed upload URL
2. Client uploads file via `PUT` directly to storage

**Benefits:**

- Offloads server bandwidth
- Highly scalable

### WebDAV

An extension of HTTP that allows file management operations.

- Methods like `PUT`, `PROPFIND`, `MOVE`
- Treats server like a filesystem

### GraphQL-based uploads (non-multipart variants)

While many GraphQL uploads still use multipart under the hood, some systems:

- Encode files as base64 in mutations
- Or use custom upload scalars with alternative transport