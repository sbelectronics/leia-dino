#! /bin/bash
SONGSET=all
if [ -f /etc/dino.conf ]; then
    source /etc/dino.conf
fi
ASOPT=""
if [ "$AUTOSHUTDOWN" == "y" ]; then
    ASOPT="--autoshutdown"
fi
INVOPT=""
if [ "$INVERT" == "y" ]; then
    INVOPT="--invert"
fi
QUIETOPT=""
if [ "$QUIET" == "y" ]; then
    QUIETOPT="--quiet"
fi
cd /home/pi/dino
nohup python ./dino.py $ASOPT $INVOPT $SONGSET $QUIETOPT > /tmp/dino.out 2> /tmp/dino.err &
