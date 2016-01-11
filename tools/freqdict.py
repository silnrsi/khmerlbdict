#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Hardwired for Khmer at the moment"""

from argparse import ArgumentParser
from math import log10
from itertools import combinations
from functools import partial
import codecs, sys, re

parser = ArgumentParser()
parser.add_argument('dicts', nargs='+', help='csv wordlists to read')
parser.add_argument('-w','--weight', action='append', type=int, help='relative weights for various wordlists')
parser.add_argument('-o','--output', help='Output file')
parser.add_argument('-n','--noexpansions', action='store_true', help="Don't create extra misspelled words")
parser.add_argument('-l','--linear', action='store_true', help='Output linear frequencies')
args = parser.parse_args()

def checkok(t, w) :
    if t.endswith(u"\u17d2") : return False
    if not all(map(lambda x: 0x1780 <= ord(x) < 0x1880, t)) : return False
    if any(map(lambda x: 0x17e0 <= ord(x) < 0x17ea, t)) : return False
    return True

if args.output :
    outfh = codecs.open(args.output, 'w', 'utf-8')
else :
    outfh = codecs.getwriter('utf-8')(sys.stdout)

d = {}
total = 0.
badcount = 0
m = None
for i in range(len(args.dicts)) :
    fh = codecs.open(args.dicts[i], 'r', 'utf-8')
    ft = 0.
    for l in fh.readlines() :
        t = l.strip().replace(u'\u200B', '')
        if t.startswith(u'\ufeff') : t = t[1:]
        if t.startswith('#') : continue
        c = t.find(",")
        if c < 0 : c = t.find("\t")
        if c > 0 :
            w = float(t[c+1:])
            t = t[0:c].rstrip()
        else :
            w = 1
        w *= (float(args.weight[i]) if args.weight is not None and i < len(args.weight) else 1.)
        if checkok(t, w) :
            # regularise coeng order. Equivs will then add the other one back
            t = re.sub(ur'([\u17B7-\u17BA\u17BE\u17C1-\u17C3])(\u17d2[\u1780-\u17A2])', 
                    ur'\2\1', t)
            if t in d :
                d[t] += w
            else :
                d[t] = w
            ft += w
            m = min(m, w) if m is not None else w
        else :
            badcount += 1
    fh.close()
    total += ft
    if args.output :
        print "Total for {} = {:f}".format(args.dicts[i], ft)

def xorval(offset, val, s) :
    t = list(s)
    t[offset] = unichr(ord(s[offset]) ^ val)
    return u"".join(t)

def swaptxt(a, b, s) :
    return s[a:b] + s[0:a]
    
equivs = [
    # (regex, index into substring to change, xor value)
    (re.compile(ur'(\u17d2[\u178a\u178f])'), 2, partial(xorval, 1, 5)),
    (re.compile(ur'(\u17d2[\u178b\u1792])'), 2, partial(xorval, 1, 0x19)),
    (re.compile(ur'([\u17b7\u17b8])'), 1, partial(xorval, 0, 15)),
    (re.compile(ur'([\u17b1\u17b3])'), 1, partial(xorval, 0, 2)),
    (re.compile(ur'(\u17cc)'), 1, partial(xorval, 0, 3)),
    (re.compile(ur'(\u17cf)'), 1, partial(xorval, 0, 2)),
    (re.compile(ur'(\u17d2[\u1780-\u17A2][\u17B7-\u17BA\u17BE\u17C1-\u17C3])'),
            3, partial(swaptxt, 2, 3)),
]

def acsum2(x) :
    a = x[0]
    yield a
    for i in range((len(x)-2)/2) :
        a += x[i*2 + 1]
        a += x[i*2 + 2]
        yield a

def procequiv(a, d, extras) :
    for e in equivs :
        if not isinstance(a, basestring) :
            if e[0] in a[1] : continue
            k = a[0]
        else :
            k = a
        s = re.split(e[0], k)
        if len(s) == 1 : continue
        inds = list(acsum2(map(len, s)))
        for i in range(len(inds)) :
            for c in combinations(inds, i+1) :
                t = k[:]
                for j in c :
                    t = t[0:j] + e[2](t[j:j+e[1]]) + t[j+e[1]:]
                if t not in d :
                    d[t] = d[k]
                if not isinstance(a, basestring) :
                    extras.append((t, a[1] + [e[0]]))
                else :
                    extras.append((t, [e[0]]))

extras = []
if not args.noexpansions :
    for k in d.keys() :
        procequiv(k, d, extras)
    for k in extras :
        procequiv(k, d, extras)

total = float(total)
scale = 255. / log10(m/total)
def scalefreq(x) :
    return x if args.linear else int(log10(x / total) * scale)

outfh.write(u"\ufeff# Combined dictionary from:\n#   " + u"\n#   ".join(args.dicts) + u"\n")
outfh.write(u"# Notice this dictionary is for word and line breaking and purposely contains spelling errors\n")
for k in sorted(d.keys()) :
    if len(k) == 0 : continue
    outfh.write(u"{} {}\n".format(k, scalefreq(d[k])))
outfh.close()
            
print "Number of bad stripped characters: {}".format(badcount)
