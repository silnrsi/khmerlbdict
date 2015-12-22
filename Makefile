all : khmerdict.txt

khmerdict.txt : src/seafreq.txt src/villages.txt src/places.txt
	python tools/freqdict.py -o $@ $^

khmerdict.dict : khmerdict.txt
	gendict --bytes --transform offset-0x1780 -c $< $@

