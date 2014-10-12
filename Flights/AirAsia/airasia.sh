#!/bin/sh

basepath=$(dirname "$0")
cd ${basepath}

source ../spider_util.sh

spiderName=AirAsia
fromCityFile=$1
toCityFile=$2

init "${fromCityFile}" "${toCityFile}"

for fromCity in $(cat ${fromCityFile});
do
    for toCity in $(cat ${toCityFile});
    do
        for date in $(echo "21" "49");
        do
            log=${fromCity}-${toCity}-${date}
            isDone=$(isSkip ${log})

            fromCity=$(echo ${fromCity} | sed 's/-/ /g')
            toCity=$(echo ${toCity} | sed 's/-/ /g')

            if [ ${isDone} -eq 0 ]; then
                ${SCRAPY} ${SCRAPY_OPTS} ${spiderName} -a fromCity="${fromCity}" -a toCity="${toCity}" -a plusDate=${date}
                ret=$?
                if [ ${ret} -eq 0 ]; then
                    success ${date} ${fromCity} ${toCity} ${log}
                    sleep 5
                else
                    fail ${ret} "${SCRAPY} ${SCRAPY_OPTS} ${spiderName} -a fromCity="${fromCity}" -a toCity="${toCity}" -a plusDate=${date}"
                fi
            else
                echo "Skip ${log}"
            fi
        done
    done
done
