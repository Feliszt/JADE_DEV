int c = 0;
JSONObject configJSON;
ArrayList<String> videoNameList = new ArrayList<String>();
String videoToPlay = "";
char[] keyboardAZERTY = {'a', 'z', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'q', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'w', 'x', 'c', 'v', 'b', 'n'};

// osc
import oscP5.*;
import netP5.*;
OscP5 oscP5;
NetAddress videoLaunchServer;

// ----
void setup() { 
  //
  size(500, 700);

  // load video names
  configJSON = loadJSONObject("../../DATA/config/calib.json");
  JSONArray videoArray = configJSON.getJSONArray("objects");
  for (int i = 0; i < videoArray.size(); i++) {
    videoNameList.add(videoArray.getJSONObject(i).getString("name"));
  }

  // osc
  oscP5 = new OscP5(this,12000);
  videoLaunchServer = new NetAddress("127.0.0.1", 8000);

  // other setups
  textSize(25);
}

// ----
void draw() { 
  // bg
  background(50);

  // videos
  float textPosX = 20;
  float textPosY = 30;
  fill(255);
  for (int i = 0; i < videoNameList.size(); i++) {
    text(videoNameList.get(i), textPosX, textPosY);
    text("->  '" + str(keyboardAZERTY[i]) + "'", textPosX + 80, textPosY);
    textPosY += 30;
  }
} 

// ----
int getMovieName(char k) {
  for (int i = 0; i < videoNameList.size(); i++) {
    if (k == keyboardAZERTY[i]) {
      return i;
    }
  }
  return -1;
}

// ----
void keyPressed() {
  int n = getMovieName(key);
  
  if (n != -1) {
    // send osc messages to remove previous video
    OscMessage myMessage = new OscMessage("/remove");
    myMessage.add(videoToPlay);
    oscP5.send(myMessage, videoLaunchServer); 
    
    // update video
    videoToPlay = videoNameList.get(n);
    
    // send osc messages to add new video
    myMessage = new OscMessage("/add");
    myMessage.add(videoToPlay);
    oscP5.send(myMessage, videoLaunchServer); 
    
    //
    println("Playing [" + videoToPlay + "]");
  }
}
