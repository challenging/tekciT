#!/bin/sh

basepath=$(dirname "$0")
cd "${basepath}"

source ../spider_util.sh

spiderName=ChinaAirline
fromCityFile=$1
toCityFile=$2

init "${fromCityFile}" "${toCityFile}"

for fromCity in $(cat ${fromCityFile});
do
    for toCity in $(cat "${toCityFile}");
    do
        for plusDate in $(echo "1" "15" "29" "43");
        do
            log=${fromCity}-${toCity}-${plusDate}
            isDone=$(isSkip ${log})

            if [ ${isDone} -eq 0 ]; then
                ${SCRAPY} ${SCRAPY_OPTS} ${spiderName} -a fromCity="${fromCity}" -a toCity="${toCity}" -a plusDate=${plusDate} -a periodType=0
                ret=$?
                if [ ${ret} -eq 0 ]; then
                    success ${plusDate} ${fromCity} ${toCity} ${log}
                    sleep 5
                else
                    fail ${ret} '${SCRAPY} ${SCRAPY} ${spiderName} -a fromCity="${fromCity}" -a toCity="${toCity}" -a plusDate=${plusDate} -a periodType=0'
                fi
                echo "${log}" >> ${logPath}
            else
                echo "Skip ${city}"
            fi
        done
    done
done
