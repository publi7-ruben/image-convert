from flask import Flask, request, send_file, render_template
from PIL import Image
import io, zipfile

app = Flask(__name__)

TARGET_SIZE = (1200, 800)

def crop_center(image, target_size):
    target_ratio = target_size[0] / target_size[1]
    img_ratio = image.width / image.height
    if img_ratio > target_ratio:
        new_height = target_size[1]
        new_width = int(img_ratio * new_height)
    else:
        new_width = target_size[0]
        new_height = int(new_width / img_ratio)
    image = image.resize((new_width, new_height), Image.LANCZOS)
    left = (new_width - target_size[0]) // 2
    top = (new_height - target_size[1]) // 2
    return image.crop((left, top, left + target_size[0], top + target_size[1]))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    files = request.files.getlist('images')
    if not files:
        return "No files uploaded!", 400

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file in files:
            img = Image.open(file.stream).convert('RGB')
            img = crop_center(img, TARGET_SIZE)

            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG', dpi=(72, 72), quality=95)
            img_bytes.seek(0)

            zip_file.writestr(file.filename.rsplit('.', 1)[0] + '.jpg', img_bytes.read())

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name='processed_images.zip'
    )

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use PORT from Render if available
    app.run(debug=False, host='0.0.0.0', port=port)

