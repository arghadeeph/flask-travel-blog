import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    if('.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS):
        return True
    return False

def upload_image(file, uploaded_folder):
    """
    Upload an image to the specified folder.

    :param file: FileStorage object from request.files['file']
    :param upload_folder: Path to upload folder, e.g., 'static/uploads/blogs'
    :return: filename if uploaded successfully, or None
    """
  
    if file and allowed_file(file.filename):
        
        filename = secure_filename(file.filename)
        os.makedirs(uploaded_folder, exist_ok=True)
        path = os.path.join(uploaded_folder, filename)
        file.save(path)
        return filename
    return None
