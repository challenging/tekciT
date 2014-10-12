#!/bin/sh

basepath=$(dirname "$0")
cd ${basepath}

source ../spider_util.sh

spiderName=Flyscoot
fromCityFile=$1
toCityFile=$2

init "${fromCityFile}" "${toCityFile}"

for fromCity in $(cat "${fromCityFile}");
do
    for toCity in $(cat ${toCityFile});
    do
        for plusDate in $(echo "7" "14" "21" "28" "35");
        do
            log=${fromCity}-${toCity}-${date}
            isDone=$(isSkip ${log})

            fromCity=$(echo ${fromCity} | sed 's/-/ /g')
            toCity=$(echo ${toCity} | sed 's/-/ /g')

            if [ ${isDone} -eq 0 ]; then
                ${SCRAPY} ${SCRAPY_OPTS} ${spiderName} -a fromCity="${fromCity}" -a toCity="${toCity}" -a plusDate=${plusDate}
                ret=$?
                if [ ${ret} -eq 0 ]; then
                    success ${plusDate} ${fromCity} ${toCity} ${log}
                    sleep 5
                else
                    fail ${ret} '${SCRAPY} ${SCRAPY} ${spiderName} -a fromCity="${fromCity}" -a toCity="${toCity}" -a plusDate=${plusDate}'
                fi
            else
                echo "Skip ${log}"
            fi
        done
    done
done
