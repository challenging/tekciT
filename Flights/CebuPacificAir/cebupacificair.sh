#!/bin/sh

basepath=$(dirname "$0")
cd ${basepath}

source ../spider_util.sh

spiderName=CebuPacificAir
fromCityFile=$1
toCityFile=$2

init "${fromCityFile}" "${toCityFile}"

for fromCity in $(cat ${fromCityFile});
do
    for toCity in $(cat ${toCityFile});
    do
        for date in $(echo "7,14" "15,22" "23,30" "31,38" "39,46");
        do
            if [ "${fromCity}" == "${toCity}" ]; then
                continue
            fi

            log=${fromCity}-${toCity}-${date}
            isDone=$(isSkip ${log})
            if [ ${isDone} -eq 0 ]; then
                dateStart=$(echo ${date} | cut -d "," -f1)
                dateEnd=$(echo ${date} | cut -d "," -f2)

                ${SCRAPY} ${SCRAPY_OPTS} ${spiderName} -a fromCity="${fromCity}" -a toCity="${toCity}" -a dateStart=${dateStart} -a dateEnd=${dateEnd}
                ret=$?
                if [ ${ret} -eq 0 ]; then
                    success ${dateStart} ${fromCity} ${toCity} ${log}
                    sleep 5
                else
                    fail ${ret} "${SCRAPY} ${SCRAPY} ${spiderName} -a fromCity="${fromCity}" -a toCity="${toCity}" -a dateStart=${dateStart} -a dateEnd=${dateEnd}"
                fi
            else
                echo "Skip ${log}"
            fi
        done
    done
done
