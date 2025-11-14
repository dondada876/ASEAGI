#!/usr/bin/env python3
"""
Ultra-simple HTML file upload server
No dependencies except Python standard library
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import cgi
import os
from pathlib import Path
from datetime import datetime

UPLOAD_DIR = Path("/home/user/ASEAGI/uploads/web_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document Upload</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 600px;
            width: 100%;
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 32px;
            text-align: center;
        }
        .subtitle {
            color: #666;
            text-align: center;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 15px;
            padding: 60px 20px;
            text-align: center;
            background: #f8f9ff;
            margin-bottom: 20px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .upload-area:hover {
            background: #f0f2ff;
            border-color: #764ba2;
        }
        .upload-area.drag-over {
            background: #e8ebff;
            border-color: #764ba2;
            transform: scale(1.02);
        }
        .upload-icon {
            font-size: 64px;
            margin-bottom: 20px;
        }
        .upload-text {
            font-size: 18px;
            color: #333;
            margin-bottom: 10px;
        }
        .upload-subtext {
            font-size: 14px;
            color: #666;
        }
        input[type="file"] {
            display: none;
        }
        .file-list {
            margin: 20px 0;
            max-height: 200px;
            overflow-y: auto;
        }
        .file-item {
            background: #f8f9ff;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .file-name {
            font-weight: 500;
            color: #333;
        }
        .file-size {
            color: #666;
            font-size: 14px;
        }
        .upload-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 18px 40px;
            font-size: 18px;
            border-radius: 12px;
            cursor: pointer;
            width: 100%;
            font-weight: 600;
            transition: transform 0.2s;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        .upload-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }
        .upload-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        .status {
            margin-top: 20px;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            font-weight: 500;
        }
        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .progress {
            margin-top: 20px;
            height: 8px;
            background: #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
            display: none;
        }
        .progress-bar {
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            width: 0%;
            transition: width 0.3s;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📁 Document Upload</h1>
        <p class="subtitle">Upload your legal documents securely</p>

        <div class="upload-area" id="uploadArea">
            <div class="upload-icon">📤</div>
            <div class="upload-text">Click to browse or drag files here</div>
            <div class="upload-subtext">PDF, JPG, PNG, TXT, DOCX supported</div>
        </div>

        <input type="file" id="fileInput" multiple
               accept=".pdf,.jpg,.jpeg,.png,.txt,.docx,.doc,.rtf">

        <div class="file-list" id="fileList"></div>

        <button class="upload-btn" id="uploadBtn" disabled>
            🚀 UPLOAD FILES
        </button>

        <div class="progress" id="progress">
            <div class="progress-bar" id="progressBar"></div>
        </div>

        <div id="status"></div>
    </div>

    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const fileList = document.getElementById('fileList');
        const uploadBtn = document.getElementById('uploadBtn');
        const status = document.getElementById('status');
        const progress = document.getElementById('progress');
        const progressBar = document.getElementById('progressBar');

        let selectedFiles = [];

        // Click to browse
        uploadArea.addEventListener('click', () => fileInput.click());

        // File selection
        fileInput.addEventListener('change', (e) => {
            handleFiles(e.target.files);
        });

        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('drag-over');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            handleFiles(e.dataTransfer.files);
        });

        function handleFiles(files) {
            selectedFiles = Array.from(files);
            displayFiles();
            uploadBtn.disabled = selectedFiles.length === 0;
        }

        function displayFiles() {
            fileList.innerHTML = '';
            selectedFiles.forEach(file => {
                const div = document.createElement('div');
                div.className = 'file-item';
                div.innerHTML = `
                    <span class="file-name">📄 ${file.name}</span>
                    <span class="file-size">${formatSize(file.size)}</span>
                `;
                fileList.appendChild(div);
            });
        }

        function formatSize(bytes) {
            if (bytes < 1024) return bytes + ' B';
            if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
            return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
        }

        uploadBtn.addEventListener('click', async () => {
            if (selectedFiles.length === 0) return;

            uploadBtn.disabled = true;
            progress.style.display = 'block';
            status.innerHTML = '';

            let uploaded = 0;

            for (let i = 0; i < selectedFiles.length; i++) {
                const file = selectedFiles[i];
                const formData = new FormData();
                formData.append('file', file);

                try {
                    const response = await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });

                    if (response.ok) {
                        uploaded++;
                    }

                    const percent = ((i + 1) / selectedFiles.length) * 100;
                    progressBar.style.width = percent + '%';

                } catch (error) {
                    console.error('Upload error:', error);
                }
            }

            progress.style.display = 'none';

            if (uploaded === selectedFiles.length) {
                status.className = 'status success';
                status.innerHTML = `✅ Successfully uploaded ${uploaded} file(s)!`;
                selectedFiles = [];
                fileList.innerHTML = '';
                uploadBtn.disabled = true;
            } else {
                status.className = 'status error';
                status.innerHTML = `⚠️ Uploaded ${uploaded} of ${selectedFiles.length} files`;
            }
        });
    </script>
</body>
</html>
"""

class UploadHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(HTML_PAGE.encode())

    def do_POST(self):
        if self.path == '/upload':
            try:
                # Parse multipart form data
                content_type = self.headers['Content-Type']
                if not content_type:
                    self.send_error(400, "No Content-Type header")
                    return

                # Get boundary
                boundary = content_type.split("boundary=")[1].encode()

                # Read the body
                content_length = int(self.headers['Content-Length'])
                body = self.rfile.read(content_length)

                # Parse multipart data
                parts = body.split(b'--' + boundary)

                for part in parts:
                    if b'filename=' in part:
                        # Extract filename
                        filename_start = part.find(b'filename="') + 10
                        filename_end = part.find(b'"', filename_start)
                        filename = part[filename_start:filename_end].decode()

                        if not filename:
                            continue

                        # Extract file content
                        content_start = part.find(b'\r\n\r\n') + 4
                        content_end = part.rfind(b'\r\n')
                        file_content = part[content_start:content_end]

                        # Save file
                        filepath = UPLOAD_DIR / filename
                        with open(filepath, 'wb') as f:
                            f.write(file_content)

                        print(f"✅ Saved: {filename} ({len(file_content)} bytes)")

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status": "success"}')

            except Exception as e:
                print(f"❌ Upload error: {e}")
                self.send_error(500, str(e))
        else:
            self.send_error(404)

    def log_message(self, format, *args):
        # Suppress default logging
        pass

def run_server(port=8506):
    server = HTTPServer(('0.0.0.0', port), UploadHandler)
    print(f"✅ Upload server running on port {port}")
    print(f"🌐 Access at: http://137.184.1.91:{port}")
    print(f"📁 Uploads saved to: {UPLOAD_DIR}")
    server.serve_forever()

if __name__ == '__main__':
    run_server()
