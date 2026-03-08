var circles = [];
var canvas;
var context;
var previousSelectedCircle;
var isDragging = false;

var pendingPoints = null;

window.onload = function(){
  canvas = document.getElementById("canvas");
  if (!canvas) return; 

  context = canvas.getContext("2d");
  canvas.onmousedown = canvasClick;
  canvas.onmouseup = stopDragging;
  canvas.onmouseout = stopDragging;
  canvas.onmousemove = dragCircle;

  if (pendingPoints !== null) {
    _doLoadPoints(pendingPoints);
  }
};


class Circle {
    constructor(x, y, radius, color) {
        this.x = x;
        this.y = y;
        this.radius = radius;
        this.color = color;
        this.isSelected = false;
    }
}


function loadImage(file){
  return new Promise((resolve, reject) => {
    let img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = file + '?t=' + Date.now();
  });
}

function loadPoints(points) {
  if (document.readyState === 'complete') {
    _doLoadPoints(points);
  } else {
    pendingPoints = points;
  }
}

function _doLoadPoints(points) {
  circles = [];
  for (var i = 0; i < points.length; i++) {
    var circle = new Circle(points[i].x, points[i].y, 10, "#d4ff47");
    circles.push(circle);
  }
  _loadAndDraw('/static/media/resize_image.jpg');
}

async function _loadAndDraw(file) {
  var canvasEl = document.getElementById("canvas");
  var ctx = canvasEl.getContext("2d");
  var loadedImg = await loadImage(file);
  canvasEl.width  = loadedImg.width;
  canvasEl.height = loadedImg.height;
  window.img = loadedImg;
  ctx.drawImage(loadedImg, 0, 0, loadedImg.width, loadedImg.height);
  drawCircles();
}

function drawCircles() {
  var canvasEl = document.getElementById("canvas");
  if (!canvasEl || !window.img) return;
  var ctx = canvasEl.getContext("2d");
  ctx.clearRect(0, 0, canvasEl.width, canvasEl.height);
  ctx.globalAlpha = 1.0;
  ctx.drawImage(window.img, 0, 0, window.img.width, window.img.height);

  ctx.globalAlpha = 0.7;
  ctx.strokeStyle = "#d4ff47";
  ctx.lineWidth = 3;
  ctx.setLineDash([6, 8]);
  ctx.beginPath();
  for (var i = 0; i < circles.length; i++) {
    var next = circles[(i + 1) % circles.length];
    if (i === 0) ctx.moveTo(circles[i].x, circles[i].y);
    ctx.lineTo(next.x, next.y);
  }
  ctx.closePath();
  ctx.stroke();
  ctx.setLineDash([]);

  for (var i = 0; i < circles.length; i++) {
    var circle = circles[i];
    ctx.globalAlpha = 1.0;
    ctx.beginPath();
    ctx.arc(circle.x, circle.y, circle.radius, 0, Math.PI * 2);
    ctx.fillStyle = circle.isSelected ? "#ffffff" : "#d4ff47";
    ctx.strokeStyle = circle.isSelected ? "#d4ff47" : "#000000";
    ctx.lineWidth = circle.isSelected ? 3 : 1.5;
    ctx.fill();
    ctx.stroke();
  }
}

function canvasClick(e) {
  var rect = canvas.getBoundingClientRect();
  var scaleX = canvas.width / rect.width;
  var scaleY = canvas.height / rect.height;
  var clickX = (e.clientX - rect.left) * scaleX;
  var clickY = (e.clientY - rect.top) * scaleY;

  for (var i = circles.length - 1; i >= 0; i--) {
    var circle = circles[i];
    var dist = Math.sqrt(Math.pow(circle.x - clickX, 2) + Math.pow(circle.y - clickY, 2));
    if (dist <= circle.radius * 2) {
      if (previousSelectedCircle != null) previousSelectedCircle.isSelected = false;
      previousSelectedCircle = circle;
      circle.isSelected = true;
      isDragging = true;
      drawCircles();
      return;
    }
  }
}


function stopDragging() {
  isDragging = false;
}

function dragCircle(e) {
  if (!isDragging || previousSelectedCircle == null) return;
  var rect = canvas.getBoundingClientRect();
  var scaleX = canvas.width / rect.width;
  var scaleY = canvas.height / rect.height;
  previousSelectedCircle.x = (e.clientX - rect.left) * scaleX;
  previousSelectedCircle.y = (e.clientY - rect.top) * scaleY;
  drawCircles();
}


$(document).ready(function(){
  $("#sendData").click(function(){
    $("#loader").html('<img src="/static/images/DocumentOCRScan.gif" style="width:60px">');
    $("#sendData").prop("disabled", true).css("opacity", "0.6");
    $.ajax({
      type: 'POST',
      url: '/transform',
      contentType: 'application/json;charset=UTF-8',
      data: JSON.stringify({
        "data": [
          [circles[0].x, circles[0].y],
          [circles[1].x, circles[1].y],
          [circles[2].x, circles[2].y],
          [circles[3].x, circles[3].y]
        ]
      }),
      success: function(response) {
        window.location.href = '/prediction';
      },
      error: function() {
        $("#loader").html('');
        $("#sendData").prop("disabled", false).css("opacity","1");
        alert('Transform failed. Please try again.');
      }
    });
  });
});
