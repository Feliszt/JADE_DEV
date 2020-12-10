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

	// load video
	videos[0]->play();
	videos[0]->setVolume(0.0);
}

//--------------------------------------------------------------
void ofApp::update(){
	// update video
	videos[0]->update();
}

//--------------------------------------------------------------
void ofApp::draw(){
	// background
	ofBackground(0);

	// play video
	videos[0]->draw(0, 0);
}

//--------------------------------------------------------------
void ofApp::keyPressed(int key){

}