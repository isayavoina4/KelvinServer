from flask import Flask, request, send_from_directory, render_template_string, redirect, url_for, flash
import os

FILES_FOLDER = os.path.join(os.getcwd(), "Files")
os.makedirs(FILES_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = FILES_FOLDER
app.secret_key = 'your_secret_key_here'  # Для використання функції flash

@app.route('/favicon.png')
def favicon():
    return send_from_directory('.', 'favicon.png')

HTML_TEMPLATE = """<!doctype html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>📁 Файловий Сервер</title>
  <link rel="icon" href="/favicon.png" type="image/png">
  <style>
    body { font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; margin: 0; }
    .container { max-width: 900px; margin: auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    h1 { color: #222; text-align: center; }
    h2 { color: #333; }
    input, button { padding: 10px; font-size: 16px; border: 1px solid #ccc; border-radius: 5px; margin-top: 10px; width: 100%; }
    a { color: #0066cc; text-decoration: none; }
    a:hover { text-decoration: underline; }
    ul { padding-left: 0; margin: 0; list-style: none; }
    li { padding: 10px; background: #f0f0f0; margin: 5px 0; border-radius: 8px; }
    .file-preview { display: flex; flex-direction: column; align-items: center; margin-top: 10px; }
    .file-preview img, .file-preview video, .file-preview audio { max-width: 200px; margin-top: 10px; }
    button.delete { background-color: red; color: white; border: none; padding: 5px 10px; cursor: pointer; margin-left: 10px; }
    button.rename, button.edit { background-color: #ff9c00; color: white; border: none; padding: 5px 10px; cursor: pointer; }
    .button-container { display: flex; justify-content: space-between; }
    .flash-message { background-color: #f8d7da; padding: 10px; margin-bottom: 15px; border: 1px solid #f5c6cb; color: #721c24; border-radius: 5px; }
    .flash-message.success { background-color: #d4edda; color: #155724; }
    .flash-message.error { background-color: #f8d7da; color: #721c24; }
    .upload-section { display: flex; justify-content: space-between; align-items: center; }
    .upload-section input[type="file"] { flex: 1; }
    @media (max-width: 600px) {
      .container { padding: 15px; }
      .upload-section { flex-direction: column; }
    }
  </style>
</head>
<body>

<div class="container">
  <h1>📁 Файловий Сервер</h1>
  {% with messages = get_flashed_messages() %}
    {% if messages %}
      <div class="flash-message {{ 'success' if 'успішно' in messages[0] else 'error' }}">
        {{ messages[0] }}
      </div>
    {% endif %}
  {% endwith %}
  
  <div class="upload-section">
    <form method="POST" enctype="multipart/form-data">
      <input type="file" name="file" multiple>
      <button type="submit">Завантажити</button>
    </form>
  </div>

  <h2>📄 Список файлів</h2>
  <ul>
    {% for file in files %}
      <li>
        <div class="file-info">
          <a href="/files/{{ file }}">{{ file }}</a>
          {% if file.endswith('.txt') %}
            <span class="button-container">
              <button class="edit"><a href="/edit/{{ file }}">Редагувати</a></button>
            </span>
          {% endif %}
          <span class="button-container">
            <button class="rename"><a href="/rename/{{ file }}">Перейменувати</a></button>
            <button class="delete"><a href="/delete/{{ file }}">Видалити</a></button>
          </span>
        </div>
        <div class="file-preview">
          {% if file.endswith('.jpg') or file.endswith('.png') %}
            <img src="/files/{{ file }}" alt="{{ file }}">
          {% elif file.endswith('.mp4') %}
            <video controls>
              <source src="/files/{{ file }}" type="video/mp4">
            </video>
          {% elif file.endswith('.mp3') %}
            <audio controls>
              <source src="/files/{{ file }}" type="audio/mp3">
            </audio>
          {% endif %}
        </div>
      </li>
    {% endfor %}
  </ul>

  <h2>🔍 Пошук файлів</h2>
  <form method="GET" action="/">
    <input type="text" name="search" placeholder="Пошук файлів..." value="{{ search_term }}">
    <button type="submit">Пошук</button>
  </form>
</div>

</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    search_term = request.args.get('search', '')
    files = [file for file in os.listdir(FILES_FOLDER) if search_term.lower() in file.lower()]
    
    if request.method == "POST" and "file" in request.files:
        for f in request.files.getlist("file"):
            f.save(os.path.join(FILES_FOLDER, f.filename))
        flash("Файл успішно завантажено!", "success")
    
    return render_template_string(HTML_TEMPLATE, files=files, search_term=search_term)

@app.route("/files/<path:filename>")
def download_file(filename):
    return send_from_directory(FILES_FOLDER, filename)

@app.route("/edit/<filename>", methods=["GET", "POST"])
def edit_file(filename):
    filepath = os.path.join(FILES_FOLDER, filename)
    if request.method == "POST":
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(request.form["content"])
        flash(f"Файл {filename} успішно оновлено!", "success")
        return redirect("/")
    else:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    return render_template_string(HTML_TEMPLATE, files=[filename], content=content, filename=filename)

@app.route("/delete/<filename>")
def delete_file(filename):
    filepath = os.path.join(FILES_FOLDER, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        flash(f"Файл {filename} успішно видалено!", "success")
    else:
        flash(f"Файл {filename} не знайдено!", "error")
    return redirect("/")

@app.route("/rename/<filename>", methods=["GET", "POST"])
def rename_file(filename):
    filepath = os.path.join(FILES_FOLDER, filename)
    if request.method == "POST":
        new_name = request.form["new_name"]
        new_filepath = os.path.join(FILES_FOLDER, new_name)
        os.rename(filepath, new_filepath)
        flash(f"Файл {filename} успішно перейменовано на {new_name}!", "success")
        return redirect("/")
    return render_template_string("""
        <form method="POST">
            <label for="new_name">Нове ім'я:</label>
            <input type="text" name="new_name" value="{{ filename }}" required>
            <button type="submit">Змінити ім'я</button>
        </form>
    """, filename=filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=26722)
#port=8080