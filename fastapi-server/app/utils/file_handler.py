def save_uploaded_file(uploaded_file, destination: str) -> str:
    with open(destination, "wb") as buffer:
        buffer.write(uploaded_file.file.read())
    return destination

def delete_file(file_path: str) -> None:
    import os
    if os.path.exists(file_path):
        os.remove(file_path)

def get_temp_file_path(file_name: str) -> str:
    import tempfile
    return tempfile.gettempdir() + "/" + file_name