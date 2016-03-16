all : khmerdict.dict

khmerdict.txt : src/seafreq.txt src/villages.txt src/places.txt src/names.txt src/KHSV.txt src/KHOV.txt src/TD.txt src/HC.txt src/DFD.txt
	python tools/freqdict.py -o $@ -w 1 -w 1 -w 20 -w 50 -w 1 -w 1 -w 10 -w 10 -w 5 $^

khmerdict.dict : khmerdict.txt
	gendict --bytes --transform offset-0x1780 -c $< $@

