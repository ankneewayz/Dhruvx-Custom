from flask import Flask, request, jsonify, render_template_string
import requests, time

app = Flask(__name__)

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>🎧  DHRUV MUSIC AI</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
  body {
    margin: 0;
    font-family: 'Poppins', sans-serif;
    background: radial-gradient(circle at top left, #764ba2, #667eea);
    color: #333;
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 30px;
  }

  .app-card {
    background: #fff;
    width: 100%;
    max-width: 780px;
    border-radius: 18px;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.25);
    padding: 40px;
    animation: fadeIn 1s ease-in-out;
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: none; }
  }

  .header {
    text-align: center;
    margin-bottom: 30px;
  }

  .header i {
    font-size: 3rem;
    color: #667eea;
  }

  .header h1 {
    margin-top: 10px;
    font-size: 2.2rem;
    color: #333;
  }

  .header p {
    color: #666;
    margin-top: 8px;
    font-size: 1.05rem;
  }

  form {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  input, textarea {
    border-radius: 12px;
    border: 2px solid #ddd;
    padding: 14px 16px;
    font-size: 1rem;
    outline: none;
    transition: 0.3s ease;
  }

  input:focus, textarea:focus {
    border-color: #764ba2;
    box-shadow: 0 0 8px rgba(118, 75, 162, 0.3);
  }

  textarea {
    resize: vertical;
    min-height: 120px;
    line-height: 1.5;
  }

  button.generate-btn {
    padding: 14px 0;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: #fff;
    border: none;
    font-size: 1.1rem;
    font-weight: 600;
    border-radius: 12px;
    cursor: pointer;
    transition: transform 0.2s ease, background 0.3s ease;
  }

  button.generate-btn:hover {
    background: linear-gradient(135deg, #5a6fcf, #5b3d87);
    transform: scale(1.03);
  }

  #statusMessage {
    margin-top: 20px;
    padding: 14px;
    border-radius: 10px;
    text-align: center;
    font-weight: 600;
    display: none;
  }

  .status-loading { background: #ebf4ff; color: #3730a3; }
  .status-success { background: #dcfce7; color: #166534; }
  .status-error { background: #fee2e2; color: #991b1b; }

  .result {
    margin-top: 30px;
    text-align: center;
    display: none;
  }

  .result img {
    max-width: 250px;
    border-radius: 12px;
    margin-bottom: 20px;
    box-shadow: 0 8px 16px rgba(118, 75, 162, 0.3);
  }

  .result h3 {
    color: #764ba2;
    font-size: 1.5rem;
    margin-bottom: 10px;
  }

  .result p {
    color: #555;
    margin-bottom: 15px;
  }

  audio {
    width: 100%;
    max-width: 400px;
    border-radius: 8px;
    margin-bottom: 15px;
  }

  #downloadBtn {
    padding: 12px 24px;
    border: none;
    border-radius: 10px;
    background: #764ba2;
    color: #fff;
    font-weight: 600;
    cursor: pointer;
    transition: 0.3s ease;
  }

  #downloadBtn:hover {
    background: #5b3d87;
    transform: scale(1.05);
  }
</style>
</head>
<body>
  <div class="app-card">
    <div class="header">
      <i class="fa-solid fa-headphones"></i>
      <h1>ABBAS MUSIC AI</h1>
      <p>Generate emotional & inspiring music powered by AI</p>
    </div>

    <form id="songForm">
      <input type="text" id="prompt" placeholder="Enter your song theme (e.g., 'love sorrow')" required>
      <textarea id="lyrics" placeholder="Enter your song lyrics here..." required></textarea>
      <button type="submit" class="generate-btn"><i class="fa-solid fa-wand-magic-sparkles"></i> Generate Song</button>
    </form>

    <div id="statusMessage"></div>

    <div class="result" id="resultContainer">
      <img id="thumbnail" src="" alt="Thumbnail">
      <h3 id="songTitle"></h3>
      <p id="songStatus"></p>
      <audio id="songAudio" controls></audio><br>
      <button id="downloadBtn"><i class="fa-solid fa-download"></i> Download</button>
    </div>
  </div>

<script>
const form = document.getElementById('songForm');
const statusMessage = document.getElementById('statusMessage');
const resultContainer = document.getElementById('resultContainer');
const thumbnail = document.getElementById('thumbnail');
const songTitle = document.getElementById('songTitle');
const songStatus = document.getElementById('songStatus');
const songAudio = document.getElementById('songAudio');
const downloadBtn = document.getElementById('downloadBtn');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  statusMessage.style.display = 'block';
  statusMessage.className = 'status-loading';
  statusMessage.innerText = '🎶 Generating your song... please wait.';
  resultContainer.style.display = 'none';

  const prompt = document.getElementById('prompt').value.trim();
  const lyrics = document.getElementById('lyrics').value.trim();

  if (!prompt || !lyrics) {
    statusMessage.className = 'status-error';
    statusMessage.innerText = 'Please provide both song theme and lyrics.';
    return;
  }

  try {
    const response = await fetch('/api/song', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({prompt, lyrics})
    });

    const result = await response.json();
    if (result.error) throw new Error(result.error);
    if (!result.music_url) throw new Error('Song generation failed.');

    thumbnail.src = result.thumbnail_url || '';
    songTitle.innerText = 'Your AI Song';
    songStatus.innerText = 'Generated successfully!';
    songAudio.src = result.music_url;

    downloadBtn.onclick = () => {
      const a = document.createElement('a');
      a.href = result.music_url;
      a.download = 'abbas_ai_song.mp3';
      a.click();
    };

    statusMessage.className = 'status-success';
    statusMessage.innerText = ' Song generated successfully!';
    resultContainer.style.display = 'block';
  } catch (err) {
    statusMessage.className = 'status-error';
    statusMessage.innerText = err.message || 'Failed to generate song.';
  }
});
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/api/song", methods=["POST"])
def generate_song():
    try:
        data = request.get_json(force=True)
        prompt = data.get("prompt", "").strip()
        lyrics = data.get("lyrics", "").strip()
        if not prompt or not lyrics:
            return jsonify({"error": "Both theme and lyrics are required."}), 400

        gen_api = "https://song-gen-api.vercel.app/"
        fetch_api = "https://songs-id-api.vercel.app/"

        gen_resp = requests.get(gen_api, params={"user_prompt": prompt, "user_lyrics": lyrics}, timeout=15)
        gen_resp.raise_for_status()
        gen_json = gen_resp.json()

        conversation_id = gen_json.get("data", {}).get("conversation_id")
        if not conversation_id:
            return jsonify({"error": "Failed to get conversation_id.", "details": gen_json}), 500

        for _ in range(10):
            fetch_resp = requests.get(fetch_api, params={"conversation_id": conversation_id}, timeout=15)
            fetch_resp.raise_for_status()
            fetch_json = fetch_resp.json()
            if fetch_json.get("code") == 100000 and "data" in fetch_json:
                data_block = fetch_json["data"]
                if data_block.get("music_url"):
                    return jsonify({
                        "success": True,
                        "music_url": data_block["music_url"],
                        "thumbnail_url": data_block.get("thumbnail_url", "")
                    })
            time.sleep(3)

        return jsonify({"error": "Song not ready yet. Please try again shortly."}), 503

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
