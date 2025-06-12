import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    if('.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS):
        return True
    return False

def upload_image(file, uploaded_folder, old_filename=None):
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

        # Delete old file if it exists and is different from new file
        if old_filename and old_filename != filename:
            delete_file(os.path.join(uploaded_folder, old_filename))

        return filename
    return None

def delete_file(filepath):
    """
    Delete a file from the filesystem.

    :param filepath: Full path to the file
    """
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
    except Exception as e:
        print(f"Error deleting file: {e}")
    return False
