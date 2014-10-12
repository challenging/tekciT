#!/bin/sh

basepath=$(dirname "$0")
cd ${basepath}

source ../spider_util.sh

spiderName=Csair
fromCityFile=$1
toCityFile=$2

init "${fromCityFile}" "${toCityFile}"

for fromCity in $(cat ${fromCityFile});
do
    fromCityCode=$(echo ${fromCity} | cut -d "," -f2)
    fromCity=$(echo ${fromCity} | cut -d "," -f1)

    for toCity in $(cat ${toCityFile});
    do
        toCityCode=$(echo ${toCity} | cut -d "," -f2)
        toCity=$(echo ${toCity} | cut -d "," -f1)

        for date in $(echo "7,45");
        do
            log=${fromCityCode}-${toCityCode}-${date}
            isDone=$(isSkip ${log})

            if [ ${isDone} -eq 0 ]; then
                dateStart=$(echo ${date} | cut -d "," -f1)
                dateEnd=$(echo ${date} | cut -d "," -f2)

                ${SCRAPY} ${SCRAPY_OPTS} ${spiderName} -a fromCity="${fromCity}" -a fromCityCode=${fromCityCode} -a toCity="${toCity}" -a toCityCode=${toCityCode} -a dateStart=${dateStart} -a dateEnd=${dateEnd}
                ret=$?
                if [ ${ret} -eq 0 ]; then
                    success ${dateStart} ${fromCity} ${toCity} ${log}
                    sleep 5
                else
                    fail ${ret} "${SCRAPY} ${SCRAPY} ${spiderName} -a fromCity=${fromCity} -a fromCityCode=${fromCityCode} -a toCity="${toCity}" -a toCityCode=${toCityCode} -a dateStart=${dateStart} -a dateEnd=${dateEnd}"
                fi
            else
                echo "Skip ${log}"
            fi
        done
    done
done
