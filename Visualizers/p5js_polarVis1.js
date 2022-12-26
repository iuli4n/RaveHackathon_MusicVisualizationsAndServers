// uses p5.Polar library


//------------- WEBSOCKET --------------
// HOW TO INTEGRATE INTO YOUR OWN SKETCH: 
//   1. Copy this part into your p5js sketch
//   2. Add ws_setup() to the setup() function as shown below
//   3. Then access the wsData1,2,3 variables

var ws_host = 'localhost:8000'; // address of the websocket server
var ws_socket; // socket we'll be using
var wsData1, wsData2, wsData3; // data we received from the socket

function ws_setup() {
  // connect to server:
  ws_socket = new WebSocket('ws://' + ws_host);
  // socket connection listener:
  ws_socket.onopen = ws_sendIntro;
  // socket message listener:
  ws_socket.onmessage = ws_readMessage;
  
  print("Websocket server started");
}

function ws_readMessage(event) {
  var msg = event.data; // read data from the onmessage event
  //print("Received: "+msg); // print it

  // Assume we're getting 3 numerical values separated by comma: X,Y,Z
  
  const arduinoDataSplit = msg.split(",");

  wsData1 = parseInt(arduinoDataSplit[0]);
  wsData2 = parseInt(arduinoDataSplit[1]);
  wsData3 = parseInt(arduinoDataSplit[2]);
}

function ws_sendIntro() {
  ws_socket.send("Hello");
}

//------------- WEBSOCKET END ----------


function setup() {
  createCanvas(800, 800);
  ws_setup();
}

let noiseTraveler = 0;

function draw() { 
  var1 = wsData1;
  var2 = wsData2;
  
  
  background(50+var1+var2);
  setCenter(width/2, height/2);
  stroke(0,0,0, 50);
  noFill();
  ellipseMode(CENTER);

  //print(millis()," ",var1);
  
  polarDrawCallback(5, 80, 50, function(i, a, r, d) {
    
    
    noFill();
    polarDrawCallback(var2/2, 5, var2*3, function(i, a, r, d) {

      stroke(i*30,50,0, 80);
      stroke(255-var1*20,255,255-var2*20,50);
      
      for (let j=1; j<2+var1/2; j++) {
        A = 5+var2*10;
        A = A/2;
        //stroke(100*i,0,0)
        ellipse(0,-j*A/1.5, j*A,j*A);
      }
      
      line(0,0, 0,var1*10)
      for (let j=0; j<var2; j++) {
        line(-5, -j*5, 5, -j*5)
      }

    });
    
    
    fill(0, var1*20,0, 30)
    for (let j=1; j<=var1/2; j++) {
      A = a/2;
      ellipse(0,d -j*A, j*A,j*A);
    }
  
  });
}

function keyPressed() {
  {
    let fs = fullscreen();
    fullscreen(!fs);
  }
}
