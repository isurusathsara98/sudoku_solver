var canvas = document.getElementById('demo-canvas');

var ctx = canvas.getContext('2d');

var width = window.innerWidth;
var height = window.innerHeight;


var mouseX = 0, mouseY = 0;

canvas.width = width;
canvas.height = height;

console.log(width)

window.onresize = function(){
  width = window.innerWidth;
		  height = window.innerHeight;
  canvas.width = width;
		  canvas.height = height;
 
}

function Circle (x, y){
  
  this.x = x + Math.random()*width/20;
  this.y = y + Math.random()*height/20;
  this.originX = this.x;
  this.originY = this.y;
  this.radius =  (Math.random()*Math.PI)*4;
  this.shadowBlur = Math.floor(Math.random() * 30) + 15;
  this.alpha = 1;
  if(x < width/6) {
    this.color='gold'
  }else if(x > width/6 && x < width/2){
    this.color = 'cyan'
  }else{
    this.color = 'magenta'
  }
}

Circle.prototype.shiftPoint = function(){
   		var self = this;
        TweenLite.to(this, 1+1*Math.random(), {x:this.originX+50+Math.random()*50,
            y: this.originY-50+Math.random()*50,

            ease:Strong.easeInOut,                                 
            onComplete: function() {
                self.shiftPoint();
            }});
}

Circle.prototype.draw = function(){
 
  ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, 2 * Math.PI, false);
            ctx.fillStyle = 'rgba(255,255,255,' + this.alpha + ')';
    							        ctx.shadowBlur = this.shadowBlur;
            ctx.shadowColor = this.color;
            ctx.fill();
  
}

Circle.prototype.getDistanceTo = function( x, y )
{
  var xs = 0;
  var ys = 0;
 
  xs = x - this.x;
  xs = xs * xs;
 
  ys = y - this.y;
  ys = ys * ys;
 
  return Math.sqrt( xs + ys );
}


var circles = []


		for(var x = 0; x<width; x = x + width/30) {
    for	(var y = 0; y<height; y = y + height/10) {
      var ball = new Circle(x, y) 
      		  ball.shiftPoint()
        circles.push(ball);
 	      
      }
 }
 
$("body").mousemove(function(e) {
  
  mouseX = e.pageX;
  mouseY = e.pageY;
   
})


function animate(){
  ctx.clearRect(0,0,width,height); 
 for(var i = 0; i < circles.length; i++){
  var distance = circles[i].getDistanceTo(mouseX, mouseY);
  if(distance > 200 && distance <400)
  {
    if(circles[i].x > mouseX){
    	   circles[i].originX -= 7;  
    }else{
      circles[i].originX += 7;
    }
    
    if(circles[i].y > mouseY){
    	   circles[i].originY -= 7;  
    }else{
      circles[i].originY += 7;
    }
    
  }

   circles[i].draw()
 }
  requestAnimationFrame(animate);
}

animate();