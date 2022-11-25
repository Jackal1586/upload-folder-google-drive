from __future__ import print_function

import io
import time

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

from google_service import get_service


def download_file(service, real_file_id, write_ptr):
    """Downloads a file
    Args:
        real_file_id: ID of the file to download
    Returns : IO object with location.

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """

    try:
        # create drive api client

        file_id = real_file_id

        # pylint: disable=maybe-no-member
        request = service.files().get_media(fileId=file_id)
        # file = io.BytesIO()
        downloader = MediaIoBaseDownload(write_ptr, request)
        done = False
        start_time = time.time_ns()
        while done is False:
            status, done = downloader.next_chunk()
            progress = int(status.progress() * 10000) / 100
            time_elapsed = (time.time_ns() - start_time) / (10 ** 9)
            print(
                f"Downloaded {progress:6}%, Time elapsed: {time_elapsed}s, Remaining {(time_elapsed * (100-progress) / progress) if progress > 0.1 else 'INF'}. ",
                end="\r",
            )

    except HttpError as error:
        print(f"An error occurred: {error}")
        file = None

    print()
    return


if __name__ == "__main__":
    service = get_service()
    output_file = "dpr_deps.7z"

    with open(output_file, "wb") as wp:
        download_file(service, "1F3b-AyknJK0ANKcjhBQSV5kPR9_TvQpS", wp)
