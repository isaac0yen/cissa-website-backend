def generate_download_link(file_url: str) -> str:
    """
    Generate a direct download link for a Google Drive file.

    Args:
        file_url (str): The URL of the Google Drive file.
    Returns:
        str: A direct download link for the file.
    """
    # Extract the file ID from the URL
    if "drive.google.com" in file_url:
        if "/d/" in file_url:
            file_id = file_url.split("/d/")[-1].split("/")[0]
        else:
            raise ValueError("Invalid Google Drive URL format.")
        
        # Construct the direct download link
        download_link = f"https://drive.google.com/uc?export=download&id={file_id}"
        return download_link
    else:
        raise ValueError("The provided URL is not a valid Google Drive link.")