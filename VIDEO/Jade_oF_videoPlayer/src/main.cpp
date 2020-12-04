#include "ofMain.h"
#include "ofApp.h"

//========================================================================
int main( ){
	// setup app
	ofGLFWWindowSettings settings;
	settings.decorated = false;
	ofCreateWindow(settings);

	// run app
	ofRunApp(new ofApp());
}
