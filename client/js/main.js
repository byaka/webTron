/****************************************/
/**********notFlash 0.31*****************/
/*******************| ||*****************/
/*******************| |bug fix***********/
/*******************| new functions******/
/*******************global version*******/ 
/****************************************/
/*********Copyright 2012, BYaka**********/
/*******Email: byaka.life@gmail.com******/
/*********Licensed with GNU GPL**********/
/****************************************/
/*============================================================*/
var output='';
var myId='';
var isStarted=false;
var player={};
var rules='';
var timeD=0;

function getmsD(){
   return getms()-timeD;
}

function redraw(){
   if(!isStarted) return;
   output.clearCanvas();
   forMe(player,function(plr){
      if(!plr) return;
      var a=plr.direction*deg2rad, b=(rules.speed/1000)*(getmsD()-plr.lineTime)
      var nX=plr.left+Math.sin(a)*b
      var nY=plr.top+Math.cos(a)*b
      obj={strokeStyle: plr.color,strokeWidth: 3,rounded: true,fromCenter: false}
      var i=1;
      forMe(plr.points,function(c){
         obj['x'+i]=c[0];
         obj['y'+i]=c[1];
         i++;
      })
      obj['x'+i]=plr.left;
      obj['y'+i]=plr.top;
      obj['x'+(i+1)]=nX;
      obj['y'+(i+1)]=nY;
      output.drawLine(obj)
            .drawEllipse({
               fillStyle: plr.color,
               strokeStyle: "black",
               strokeWidth: 3,
               x: nX-4, y: nY-4,
               width: 8,
               height: 8,
               fromCenter: false
            });
      if(myId==plr.id) output.drawText({fillStyle: "#000",strokeStyle: "#fff",strokeWidth: 1,x: nX+Math.cos(a)*11, y: nY+Math.sin(a)*11,font: "12px Arial",text: "ME",fromCenter: false});
   },true)
}

$(document).ready(function(){
   output=$('canvas#output');
   var conn=new SockJS('http://'+prompt("Input server's adress",'127.0.0.1')+':8081/play');

   $(document).keyboard('a,w,s,d',{preventDefault:true},function(e){
      if(myId!=='watcher' && isStarted)
         conn.send(JSON.stringify({'type':'kbEvent','timestamp':getmsD(),'data':String.fromCharCode(e[0].keyCode)}));
   });

   conn.onopen=function(e){}
   
   conn.onmessage=function(e){
console.log('recivedData',e.data)
      var msg=JSON.parse(e.data);
      if(msg.type=='idSet') myId=msg.data;
      else if(msg.type=='timeSync') timeD=getms()-msg.data;
      else if(msg.type=='playerSet') player[msg.data.id]=msg.data;
      else if(msg.type=='playerDie') player[msg.data]=undefined;
      else if(msg.type=='gameSet') isStarted=msg.data;
      else if(msg.type=='ruleSet'){
         rules=msg.data;
         output.attr('width',rules.width).attr('height',rules.height);
      }
   }
   
   conn.onclose=function(e){isStarted=false}
   setInterval(redraw,30);
});