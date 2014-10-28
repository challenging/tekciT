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
        countEmpty=0
        #for date in $(echo "7,14" "15,22" "23,30" "31,38" "39,46");
        for date in $(seq 7 46);
        do
            if [ ${countEmpty} -ge 7 ]; then
                echo "The empyt count is up to upper-bound so break it!"
                break
            elif [ "${fromCity}" == "${toCity}" ]; then
                break
            fi

            log=${fromCity}-${toCity}-${date}
            isDone=$(isSkip ${log})
            if [ ${isDone} -eq 0 ]; then
                #dateStart=$(echo ${date} | cut -d "," -f1)
                #dateEnd=$(echo ${date} | cut -d "," -f2)

                dateStart=${date}
                dateEnd=${date}

                ${SCRAPY} ${SCRAPY_OPTS} ${spiderName} -a fromCity="${fromCity}" -a toCity="${toCity}" -a dateStart=${dateStart} -a dateEnd=${dateEnd}
                ret=$?
                if [ ${ret} -eq 0 ]; then
                    c=$(success ${dateStart} ${fromCity} ${toCity} ${log} | tail -n 1)
                    if [ ${c} -eq 0 ]; then
                        countEmpty=$(expr ${countEmpty} + 1)
                    else
                        countEmpty=0
                        sleep 2
                    fi
                else
                    fail ${ret} "${SCRAPY} ${SCRAPY} ${spiderName} -a fromCity="${fromCity}" -a toCity="${toCity}" -a dateStart=${dateStart} -a dateEnd=${dateEnd}"
                fi
            else
                echo "Skip ${log}"
            fi
        done
    done
done
