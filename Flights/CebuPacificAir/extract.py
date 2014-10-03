#!/usr/bin/python

import re, sys

if __name__ == "__main__":
    for line in sys.stdin:
        results = re.findall(r'"StationCode":"([A-Z]{3})"', line)
        for result in results:
            print result
