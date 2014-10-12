#-*- coding: utf-8 -*-
#!/usr/bin/python

import os, sys
import re

if __name__ == "__main__":
    with open(sys.argv[1]) as HTML:
        text = HTML.read()

        # <li class="li" code="VIE#" region="EU" nation="AT" citycode="VIE"><span>维也纳</span></li>

        for line in text.split("</li>"):
            if line.strip() == "":
                continue

            results = re.findall('<li class="li" code="([\w#]{4})" region="(\w{2})" nation="(\w{2})" citycode="(\w{3})"><span>(.*)</span>', line)
            a = list(results[0])
            wanted = [a[4], a[0], a[2], a[1], a[3]]
            line = ",".join(wanted)
            print line.replace("#", "")
