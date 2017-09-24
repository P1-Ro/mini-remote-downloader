# Mini Remote Downloader
A simple web app to help you download files on server, it's like a proxyed downloader, useful when certain sites are blocked.

## Deploy

0. Clone this repo
    ```
    git clone https://github.com/aulphar/remote-downloader.git
    ```

1. Replace placeholders for userName, password, and output directory
    ```
    return username == '{UserName}' and password == '{Password}'
    PATH_TO_SAVE = "{PATH}"
    ```
    
2. Start python app
    ```
    python app.py
    ```
    
## Usage
To start downloading simply make `POST` request on server with JSON looking like this:
```
{
    url: "http://example.com"
}
``` 
And also use `Authorization` header with same userName and password you set in `app.py`

If dowloading started successfully Status code **`200`** will be returned, otherwise Status code will be **`409`** with actual error message in `JSON`.