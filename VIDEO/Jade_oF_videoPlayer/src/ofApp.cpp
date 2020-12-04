#include "ofApp.h"

//--------------------------------------------------------------
void ofApp::setup(){
	// setup window size
	ofSetWindowShape(1920, 1080);
	ofSetWindowPosition(0, 0);

	// transform relative path to absolute
	ofFilePath path_temp;
	dataFolderRelative = "../../../DATA/videos/placeholders/";
	string dataFolderAbsolute = path_temp.getAbsolutePath(dataFolderRelative, false);

	// load videos
	ofDirectory dataFolder(dataFolderAbsolute);
	dataFolder.listDir();
	// loop through all files
	for (int i = 0; i < dataFolder.size(); i++) {
		// append to vector of video players
		ofVideoPlayer * vPlayer_temp = new ofVideoPlayer();
		vPlayer_temp->load(dataFolder.getPath(i));
		videos.push_back(vPlayer_temp);

		// debug
		ofLog() << "Loading video [" << dataFolder.getPath(i) << "]";
	}
}

//--------------------------------------------------------------
void ofApp::update(){

}

//--------------------------------------------------------------
void ofApp::draw(){

}

//--------------------------------------------------------------
void ofApp::keyPressed(int key){

}