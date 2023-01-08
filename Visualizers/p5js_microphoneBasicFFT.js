// Created by Iulian Radu, a version also available at https://editor.p5js.org/julesra/sketches/BPpoYd05x
//
// Reads audio from the microphone and plots the frequencies
// By moving the mouse you can select a specific frequency (by index = mouse x position) and see how it changes
// This is useful if you're making a sound visualizer that responds to a specific frequency

let mic, fft;

function setup() {
  createCanvas(710, 400);
  noFill();

  mic = new p5.AudioIn();
  mic.start();
  fft = new p5.FFT();
  fft.setInput(mic);
}

// keeps track of the signal at a specific frequency
plotArray = Array(40);
function plotNew(val) {
  plotArray.shift();
  plotArray.push(val);
  
  stroke(255,0,0);
  beginShape();
  for (i = 0; i < plotArray.length; i++) {
    vertex(mouseX+plotArray.length-i, map(plotArray[i], 0, 255, 30, 0));
  }
  endShape();
}

function draw() {
  background(200);

  let spectrum = fft.analyze();

  stroke(0,0,0);
  beginShape();
  for (i = 0; i < spectrum.length; i++) {
    vertex(i, map(spectrum[i], 0, 255, height, 0));
  }
  endShape();
  
  fill(0);
  text(mouseX, mouseX+5,50)
  noFill();
  line(mouseX,height, mouseX,0);
  
  // track the spectrum at the specific index
  plotNew(spectrum[mouseX]);
}