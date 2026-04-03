from flask import Flask, request, render_template_string
import requests
import re
import os

app = Flask(__name__)
app.secret_key = "tiktok-pro-downloader-2026"

# ================== Adsterra Banner ==================
ADSTERRA_BANNER = """
<script>
  atOptions = {
    'key' : '3c0625ce230375b06659da247c0b89a2',
    'format' : 'iframe',
    'height' : 60,
    'width' : 468,
    'params' : {}
  };
</script>
<script src="https://considerableinsanityaside.com/3c0625ce230375b06659da247c0b89a2/invoke.js"></script>
<script src="https://considerableinsanityaside.com/04/d8/1e/04d81e8c0d71d5f1e9c2437fc3fbc5c9.js"></script>
"""
# ====================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TikTok Downloader</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #00f2ea 0%, #ff00cc 100%);
            color: white;
            min-height: 100vh;
            font-family: 'Segoe UI', sans-serif;
            margin: 0;
            padding: 0;
        }
        .hero { 
            padding: 40px 15px 20px; 
            text-align: center; 
        }
        .card {
            background: rgba(255,255,255,0.97);
            color: #333;
            border-radius: 20px;
            box-shadow: 0 15px 30px rgba(0,0,0,0.2);
            margin: 0 10px;
            padding: 20px 15px;
        }
        .input-group .form-control {
            border-radius: 50px 0 0 50px;
            border: 2px solid #00f2ea;
            height: 50px;
        }
        .btn-primary { 
            border-radius: 0 50px 50px 0; 
            padding: 0 25px; 
            height: 50px;
        }
        .paste-btn {
            border-radius: 50px 0 0 50px;
            border: 2px solid #00f2ea;
            border-right: none;
            height: 50px;
        }
        .refresh-btn {
            width: 38px;
            height: 38px;
            border-radius: 50%;
            background: #00f2ea;
            color: white;
            border: none;
            font-size: 17px;
        }
        .ad-container {
            margin: 12px 0;
            padding: 6px;
            background: #f8f9fa;
            border-radius: 10px;
            text-align: center;
            overflow: hidden;
        }
        .loading {
            display: none;
            text-align: center;
            margin: 15px 0;
        }
        .spinner {
            width: 34px;
            height: 34px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #00f2ea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 8px;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
    """ + ADSTERRA_BANNER + """
</head>
<body>
<div class="hero">
    <h1 class="display-4 fw-bold mb-1">
        <i class="fas fa-music"></i> TikTok Downloader
    </h1>
    <p class="lead mb-0">No Watermark • HD Quality • Fast</p>
</div>

<div class="container">
    <div class="row justify-content-center">
        <div class="col-12 col-md-10 col-lg-8">
            <div class="card">

                <!-- Refresh -->
                <div class="d-flex justify-content-end mb-2">
                    <button onclick="refreshPage()" class="refresh-btn">
                        <i class="fas fa-sync-alt"></i>
                    </button>
                </div>

                <!-- Top Banner (মাথার নিচে) -->
                <div class="ad-container">
                    """ + ADSTERRA_BANNER + """
                </div>

                <form id="downloadForm" method="POST">
                    <div class="input-group">
                        <input type="text" id="url" name="url" class="form-control" 
                               placeholder="Paste TikTok video URL here..." required>
                        <button type="button" onclick="pasteFromClipboard()" class="btn paste-btn">
                            <i class="fas fa-paste"></i>
                        </button>
                        <button type="submit" id="searchBtn" class="btn btn-primary">Search</button>
                    </div>
                </form>

                <!-- Loading -->
                <div id="loading" class="loading">
                    <div class="spinner"></div>
                    <p class="text-muted fw-bold">Processing your video...</p>
                </div>

                {% if error %}
                <div class="alert alert-danger mt-3">{{ error }}</div>
                {% endif %}

                {% if download_link %}
                <div class="mt-4 text-center">
                    <h5 class="text-success mb-3">
                        <i class="fas fa-check-circle"></i> Video Found Successfully!
                    </h5>
                    {% if title %}<h6 class="mb-3 text-dark">{{ title }}</h6>{% endif %}
                    
                    {% if thumbnail %}
                    <img src="{{ thumbnail }}" class="img-fluid rounded mb-3" style="max-height: 340px; width:100%; object-fit:cover;">
                    {% endif %}

                    <a href="{{ download_link }}" target="_blank" 
                       class="btn btn-success btn-lg w-100 py-3">
                        <i class="fas fa-download"></i> Download HD (No Watermark)
                    </a>
                </div>

                <!-- Bottom Banner -->
                <div class="ad-container mt-4">
                    """ + ADSTERRA_BANNER + """
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script>
    function pasteFromClipboard() {
        navigator.clipboard.readText()
            .then(text => document.getElementById('url').value = text.trim())
            .catch(() => alert("Paste করতে সমস্যা হয়েছে।"));
    }

    function refreshPage() {
        window.location.reload();
    }

    document.getElementById('downloadForm').addEventListener('submit', function() {
        document.getElementById('loading').style.display = 'block';
        document.getElementById('searchBtn').disabled = true;
    });
</script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        if not url:
            return render_template_string(HTML_TEMPLATE, error="TikTok লিংক দিন!")

        try:
            headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36", "Referer": "https://ssstik.io/"}
            
            response = requests.post("https://ssstik.io/abc?url=dl", data={"url": url, "locale": "en"}, headers=headers, timeout=20)
            html = response.text
            download_match = re.search(r'href="(https?://[^"]+\.mp4[^"]*)"', html)
            
            if download_match:
                download_link = download_match.group(1)
                title_match = re.search(r'<p class="[^"]*title[^"]*">([^<]+)', html)
                title = title_match.group(1).strip() if title_match else "TikTok Video"
                return render_template_string(HTML_TEMPLATE, download_link=download_link, title=title)

            resp = requests.get(f"https://tikwm.com/api/?url={url}&hd=1", headers=headers, timeout=15)
            json_data = resp.json()
            if json_data.get("code") == 0:
                download_link = json_data.get("data", {}).get("play")
                title = json_data.get("data", {}).get("title", "TikTok Video")
                thumbnail = json_data.get("data", {}).get("cover")
                if download_link:
                    return render_template_string(HTML_TEMPLATE, download_link=download_link, title=title, thumbnail=thumbnail)

            return render_template_string(HTML_TEMPLATE, error="এই ভিডিও ডাউনলোড করা যায়নি। অন্য লিংক ট্রাই করুন।")

        except Exception:
            return render_template_string(HTML_TEMPLATE, error="সমস্যা হয়েছে। আবার চেষ্টা করুন।")

    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    os.makedirs('static', exist_ok=True)
    print("🚀 TikTok Downloader চালু (Compact + Adsterra)")
    print("http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
