# Mini Remote Downloader [![Codacy Badge](https://api.codacy.com/project/badge/Grade/661394942cb245c48732f46b255c33b3)](https://www.codacy.com/app/theglow666/mini-remote-downloader?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=TheGlow666/mini-remote-downloader&amp;utm_campaign=Badge_Grade) 
A simple web app to help you download files on server, it's like a proxyed downloader, useful when certain sites are blocked.
Built with as little dependencies as possible.

## Deploy

0. Clone this repo
    ```
    git clone https://github.com/aulphar/remote-downloader.git
    ```

1. Replace placeholders for PATH_TO_SAVE,  user and password
    ```
    PATH_TO_SAVE = "{PATH}"
    user = '{UserName}'
    password = '{Password}'
    ```
    
2. Start python app
    ```
    python app.py
    ```
    
## Usage
To start downloading simply make `POST` request on server with JSON looking like this:
```
{
    "url": "http://example.com",     // url to be downloaded
    "name": "example" [optional],    // new name of downloaded file
    "category": "example" [optional] // subfolder in downloads folder
}
``` 
And also use `Authorization` header with same `{UserName}` and `{Password}` you set in `app.py`

If dowloading started successfully Status code **`200`** will be returned, otherwise Status code will be **`409`** with actual error message in `JSON`.

## TODO

- Add support for downloading videos from Youtube
- Add support for downloading videos from OpenLoad