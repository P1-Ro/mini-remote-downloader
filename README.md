# Mini Remote Downloader [![Codacy Badge](https://api.codacy.com/project/badge/Grade/661394942cb245c48732f46b255c33b3)](https://www.codacy.com/app/theglow666/mini-remote-downloader?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=TheGlow666/mini-remote-downloader&amp;utm_campaign=Badge_Grade) 
A simple web app to help you download files on server, it's like a proxyed downloader, useful when certain sites are blocked.
Built with as little dependecies as possible.
**Optionally** supports downloading from [Youtube](http://youtube.com)/[Openload](https://openload.co/) and sending notification via [PushBullet](https://www.pushbullet.com)

## Deploy

0. Clone this repo
    ```
    git clone https://github.com/P1-Ro/mini-remote-downloader.git
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

## Optional

### Enable downloading from Youtube and Openload
If you want to be able download videos from youtube you need to perform these 2 steps.

 1) Install youtube-dl
 ```
 pip install youtube-dl
 ```
 2) Install PhantomJs
    
    [Instalation for Linux](https://gist.github.com/julionc/7476620)
    
    [Instalation for Windows](https://www.joecolantonio.com/2014/10/14/how-to-install-phantomjs/)
    
 ### Enable notifications via PushBullet
 If you want also get notification on your mobile phone or PC after download is complete perform these steps.
 
 1) Install pushbullet.py
 ```
 pip install pushbullet.py
 ``` 
 2) Set flag `notify_via_pushbullet` to `True`
 3) Set `pushbullet_token` to your Access Token which you can get [here](https://www.pushbullet.com/#settings)
 
 ## TODO
 
 - Extract all settings to single file instead of app.py