# -*- Makefile -*-

# Fixme: task

####################################################################################################

all: application.rcc Ressource.py

####################################################################################################

%.rcc : %.qrc
	rcc-qt5 -binary $< -o $@

Ressource.py : application.qrc
	pyrcc5 -o $@ $<

####################################################################################################

clean:
	rm *.py *.rcc
