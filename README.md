# Mini Remote Downloader [![Codacy Badge](https://api.codacy.com/project/badge/Grade/661394942cb245c48732f46b255c33b3)](https://www.codacy.com/app/theglow666/mini-remote-downloader?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=TheGlow666/mini-remote-downloader&amp;utm_campaign=Badge_Grade) [![GPA](https://codeclimate.com/github/P1-Ro/mini-remote-downloader.svg)](https://codeclimate.com/github/P1-Ro/mini-remote-downloader) [![codecov](https://codecov.io/gh/P1-Ro/mini-remote-downloader/branch/master/graph/badge.svg)](https://codecov.io/gh/P1-Ro/mini-remote-downloader) [![Build Status](https://travis-ci.org/P1-Ro/mini-remote-downloader.svg?branch=master)](https://travis-ci.org/P1-Ro/mini-remote-downloader) 
A simple web app to help you download files on server, it's like a proxyed downloader, useful when certain sites are blocked or you just want download files at home or wherever you are.
Built with as little dependecies as possible.

**Optionally** supports downloading video or audio from [Youtube](http://youtube.com)/[Openload](https://openload.co/) and sending notification via [PushBullet](https://www.pushbullet.com).
It is protected by `Basic Auth` and each user can be notified individually.

## Deploy

0. Clone this repo
    ```
    git clone https://github.com/P1-Ro/mini-remote-downloader.git
    ```

1. Replace placeholders in `config.yml`
    ```
    path: PATH
    username: USERNAME
    password: PASSWORD
    ```
    
2. Start python app
    ```
    python app.py
    ```
    
## Usage

You can use included web interface or via `POST` request.

### Web Interface
Navigate your browser to `http://{SERVER_ADDRESS}:9000`, browser will ask you for username and password. After login you can start downloading.
Here is screenshot: 

![Screenshot of web interface](https://github.com/P1-Ro/mini-remote-downloader/blob/master/screenshot.png)

### Request
To start downloading simply make `POST` request on `http://{SERVER_ADDRESS}/download/` with JSON which looks like this:
```
{
    "url": "http://example.com",     // url to be downloaded
    "name": "example" [optional],    // new name of downloaded file
    "category": "example" [optional] // subfolder in downloads folder
    "audioOnly": true [optional]     // if you want to download only audio from Youtube
}
``` 
And also use `Authorization` header with same `USERNAME` and `PASSWORD` you set in `confix.yml` , otherwise you will get **`401 Unathorized`** response

If dowloading started successfully Status code **`200`** will be returned, otherwise Status code will be **`500`** with actual error message in `JSON`.

## Optional

### Enable downloading from Youtube and Openload
If you want to be able download videos from youtube you need to perform these steps.

 1) Install youtube-dl
 ```
 pip install youtube-dl
 ```
 2) _[Optional]_ Install PhantomJs if you want to download from Openload:
    
    [Instalation for Linux](https://gist.github.com/julionc/7476620)
    
    [Instalation for Windows](https://www.joecolantonio.com/2014/10/14/how-to-install-phantomjs/)
    
 3) _[Optional]_ Install [FFmpeg](https://www.ffmpeg.org/) if you want to download mp3 from Youtube
 
    [Instalation guid for Linux and Windows](https://github.com/adaptlearning/adapt_authoring/wiki/Installing-FFmpeg)
   
 
 
 ### Enable notifications via PushBullet
 If you want also get notification on your mobile phone or PC after download is complete perform these steps.
 
 1) Install pushbullet.py
 ```
 pip install pushbullet.py
 ``` 
 2) Set flag `notify_via_pushbullet` in `config.yml` to `True`
 3) Set `pushbullet_token` in `config.yml` to your Access Token which you can get [here](https://www.pushbullet.com/#settings)
 4) Repeat steps 2 and 3 for every user you want to get notified.
