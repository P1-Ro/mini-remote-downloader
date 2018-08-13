
const nodes = {};

function updateNode(data){
    let node = nodes[data.filename];

    if(data.status === "downloading"){
        $(node).find(".file-stats .time").html(data.eta);
        $(node).find(".file-stats .speed").html(data.speed);
        let progressBar = $(node).find(".progress");
        $(progressBar).children().first().css("width", data.progress);
        progressBar.next().html(data.progress);
    }
}

function createNode(data){
    let node = $("#templateCard").clone();
    node.removeClass("hide");

    let delimiter = data.filename.indexOf("/") === -1 ? "\\" : "/";

    let arr = data.filename.split(delimiter);
    let filename = arr[arr.length -1];
    let directory = arr[arr.length -2];
    arr.splice(-1,1);
    let fullPath = arr.join(delimiter);

    let name = $(node).find(".file-name");
    name.html(filename);
    name.prop("title", filename);

    let path = $(node).find(".file-category .path");
    path.html(directory);
    path.prop("title", fullPath);

    let size = data.size ? data.size : data["_total_bytes_str"];
    $(node).find(".file-stats .size-total").html(size);

    $(".container").prepend(node);
    nodes[data.filename] = node;
}

$(function () {

    const url = window.location.origin;
    const socket = io(url);

    socket.on("connect", function () {
       socket.emit("get_downloads", function (data) {
           for(let key in data){
               if(data.hasOwnProperty(key)){
                 let curr = data[key];
                 createNode(curr);
                  socket.on(curr.filename, updateNode);
               }
           }
       });
    });

    socket.on("new_download", function (data) {
        createNode(data);
        socket.on(data.filename, updateNode);
    });

});