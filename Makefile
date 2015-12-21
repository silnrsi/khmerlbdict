all : khmerdict.txt

khmerdict.txt : src/seafreq.txt src/villages.txt src/places.txt
	python tools/freqdict.py -o $@ $^

