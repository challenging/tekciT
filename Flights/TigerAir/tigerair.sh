#!/bin/sh

basepath=$(dirname "$0")
cd ${basepath}

fromCityFile=$1
if [ ! -e ${fromCityFile} ]; then
    echo "Not Found ${fromCityFile}"
    exit 1
fi

toCityFile=$2
if [ ! -e "${toCityFile}" ]; then
    echo "Not Found ${toCityFile}"
    exit 2
fi

spiderName=TigerAir
today=$(date +%Y%m%d)

jobPath=${spiderName}/${today}
mkdir -p ${jobPath}/json

logPath=${spiderName}.${today}.log
touch ${logPath}

for fromCity in $(cat ${fromCityFile});
do
    for toCity in $(cat ${toCityFile});
    do
        for date in $(echo "7,22" "23,45");
        do
            log=${fromCity}-${toCity}-${date}

            isDone=$(grep "${log}" ${logPath} | wc -l)
            isDone=$(printf "%d" ${isDone})

            if [ ${isDone} -eq 0 ]; then
                dateStart=$(echo ${date} | cut -d "," -f1)
                dateEnd=$(echo ${date} | cut -d "," -f2)

                /usr/local/bin/scrapy crawl ${spiderName} -a fromCity="${fromCity}" -a toCity="${toCity}" -a dateStart=${dateStart} -a dateEnd=${dateEnd}
                ret=$?
                if [ ${ret} -eq 0 ]; then
                    jsonFile=${spiderName}.${dateStart}.${fromCity}.${toCity}.json

                    if [ -s "${spiderName}.${today}.json" ]; then
                        mv ${spiderName}.${today}.json ${jsonFile}
                        mv ${jsonFile} ${jobPath}/json
                    else
                        echo "Empty Results - ${spiderName}.${today}.json"
                        rm "${spiderName}.${today}.json"
                    fi

                    echo "${log}" >> ${logPath}
                    sleep 5
                else
                    echo "Fail(ret=${ret} - scrapy crawl ${spiderName} -a fromCity=${fromCity} -a toCity=${toCity} -a dateStart=${dateStart} -a dateEnd=${dateEnd})"
                    exit 999
                fi
            else
                echo "Skip ${log}"
            fi
        done
    done
done
