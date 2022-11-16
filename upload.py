from google_my import get_service
from googleapiclient.http import MediaFileUpload
from tabulate import tabulate
import mimetypes
import sys
from pathlib import Path
import os
from tqdm import tqdm
from googleapiclient.errors import HttpError

def search(service, query):
    # search for the file
    result = []
    page_token = None
    while True:
        response = service.files().list(q=query,
                                        spaces="drive",
                                        fields="nextPageToken, files(id, name, mimeType)",
                                        pageToken=page_token).execute()
        # iterate over filtered files
        for file in response.get("files", []):
            result.append((file["id"], file["name"], file["mimeType"]))
        page_token = response.get('nextPageToken', None)
        if not page_token:
            # no more files
            break
    return result

def create_folder(service, folder_name: str, parent_folder_id: str) -> str:
    """ Create a folder and prints the folder ID
    Returns : Folder Id

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    try:
        # create drive api client
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_folder_id]
        }

        # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata, fields='id'
                                      ).execute()
        print(F'Created Folder {folder_name} got ID: "{file.get("id")}".')
        return file.get('id')

    except HttpError as error:
        print(F'An error occurred: {error}')
        return None


def upload_file(service, file_to_upload, parent_folder_id: str):
    """
    Creates a folder and upload a file to it
    """
    path_to_file = Path(file_to_upload).resolve()
    if not path_to_file.exists():
        raise FileNotFoundError(f"{path_to_file} doesn't exist. Check if you provided the correct path.")
    # authenticate account
    # folder details we want to make
    
    # print(mimetypes.guess_type("test.cpp"))

    # print("Folder ID:", folder_id)
    # upload a file text file
    # first, define file metadata, such as the name and the parent folder ID
    file_metadata = {
        "name": path_to_file.name,
        "parents": [parent_folder_id],
        "mimeType": mimetypes.guess_type(path_to_file.as_uri())
    }
    # upload
    media = MediaFileUpload(path_to_file.name, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(F"File {file_to_upload} created, id:", file.get("id"))

def upload_walk(local_dir: str, service, upload_folder_id):
    folder_id_memo = dict()
    walk_itr = tqdm(os.walk(local_dir))
    for root, dirs, files in walk_itr:
        walk_itr.set_description(F"Uploading from {root}")
        for dir in tqdm(dirs, desc="Creating folders", leave=False):
            folder_id_memo[os.path.join(root, dir)] = create_folder(service, dir, folder_id_memo.get(root, upload_folder_id))

        for file in tqdm(files, desc="Uploading files", leave=False):
            upload_file(service, os.path.join(root, file), folder_id_memo.get(root, upload_folder_id))

def main(*args):
    service = get_service()
    # upload_files(service)
    file_to_upload = args[1]
    upload_folder_id = args[2]
    print(upload_folder_id)
    # upload_walk(file_to_upload,  service, upload_folder_id)

    # filter to text files
    # filetype = "text/plain"
    # # authenticate Google Drive API
    # # service = get_gdrive_service()
    # # search for files that has type of text/plain
    # search_result = search(service, query=f"")
    # # convert to table to print well
    # table = tabulate(search_result, headers=["ID", "Name", "Type"])
    # print(table)


if __name__ == "__main__":
    main(*sys.argv)
