#!/bin/sh

basepath=$(dirname "$0")
cd ${basepath}

source ../spider_util.sh

spiderName=EvaAirline
fromCityFile=$1
toCityFile=$2

init "${fromCityFile}" "${toCityFile}"

fromArea=$(basename ${fromCityFile} | cut -d "." -f1 | cut -d "_" -f2)

for fromCity in $(cat ${fromCityFile});
do
    for date in $(echo "7,45");
    do
        log=${fromCity}-${date}
        isDone=$(isSkip ${log})

        if [ ${isDone} -eq 0 ]; then
            dateStart=$(echo ${date} | cut -d "," -f1)
            dateEnd=$(echo ${date} | cut -d "," -f2)

            ${SCRAPY} ${SCRAPY_OPTS} ${spiderName} -a fromCity="${fromCity}" -a fromArea="${fromArea}" -a dateStart=${dateStart} -a dateEnd=${dateEnd}
            ret=$?
            if [ ${ret} -eq 0 ]; then
                success ${dateStart} ${fromCity} ${toCity} ${log}
                sleep 5
            else
                fail ${ret} '${SCRAPY} ${SCRAPY} ${spiderName} -a fromCity="${fromCity}" -a fromArea="${fromArea}" -a dateStart=${dateStart} -a dateEnd=${dateEnd}'
            fi
        else
            echo "Skip ${log}"
        fi
    done
done
