#!/bin/sh

# get rid of the cursor so we don't see it when videos are running
setterm -cursor off

# set here the path to the directory containing your videos
VIDEOPATH="../../DATA/videos/others/" 
while true;
do
  for videos in $VIDEOPATH/*
    do
      omxplayer $videos >/dev/null
    done
done
