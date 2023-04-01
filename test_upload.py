import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

folder_path = "C:/Users/mason/Documents/data_projects/blue_alliance_webcrawler/"
credentials_json = 'client_secret_398716151789-53pal0sfdgbmnfv7fbdvupp768lhdaqo.apps.googleusercontent.com.json'
credentials_pickle = 'token.pickle'

def get_creds():
    creds = None
    # Obtain OAuth token / user authorization.
    if os.path.exists(folder_path + credentials_pickle):
        with open(folder_path + credentials_pickle, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("starting...")
            flow = InstalledAppFlow.from_client_secrets_file(
                folder_path + credentials_json, SCOPES)
            creds = flow.run_local_server(port=0)
            print("never get here...")
        # Save the credentials for the next run
        with open(folder_path + credentials_pickle, 'wb') as token:
            pickle.dump(creds, token)
    return creds


def main():
    creds = get_creds()

    # Build the drive service.
    drive_service = build('drive', 'v3', credentials=creds)

    # Get the drive ID of the first shared drive. You can introspect the
    # 'results' dict  here to get the right shared drive if it's not the first
    # one.
    results = drive_service.drives().list(pageSize=10).execute()
    shared_drive_id = results['drives'][0]['id']#"1igMmF76MoJPO3iGYYdP4T_h0bXZR2-Hs"

    # Create the request metatdata, letting drive API know what it's receiving.
    # In this example, we place the image inside the shared drive root folder,
    # which has the same ID as the shared drive itself, but we could instead
    # choose the ID of a folder inside the shared drive.
    file_metadata = {
        'name': 'test.parquet.gzip',
        'mimeType': 'parquet',
        'parents': [shared_drive_id]}

    # Now create the media file upload object and tell it what file to upload,
    # in this case, "wakeupcat.jpg"
    media = MediaFileUpload(folder_path + 'test.parquet.gzip',
                            mimetype='parquet')

    # Upload the file, making sure supportsAllDrives=True to enable uploading
    # to shared drives.
    f = drive_service.files().create(
        body=file_metadata, media_body=media, supportsAllDrives=True).execute()

    print("Created file '%s' id '%s'." % (f.get('name'), f.get('id')))
    return


if __name__ == '__main__':
    main()