#!/bin/sh

basepath=$(dirname "$0")
cd ${basepath}

fromCityFile=$1
if [ ! -s "${fromCityFile}" ]; then
    echo "Not Found - ${fromCityFile}"
    exit 1
fi

toCityFile=$2
if [ ! -s "${toCityFile}" ]; then
    echo "Not Found - ${toCityFile}"
    exit 1
fi

spiderName=VanillaAir
today=$(date +%Y%m%d)

jobPath=${spiderName}/${today}
mkdir -p ${jobPath}/json

logPath=${spiderName}.${today}.log
touch ${logPath}

for fromCity in $(cat "${fromCityFile}");
do
    for toCity in $(cat ${toCityFile});
    do
        for date in $(echo "10" "17" "24" "31" "38" "45");
        do
            log=${fromCity}-${toCity}-${date}

            isDone=$(grep "${log}" ${logPath} | wc -l)
            isDone=$(printf "%d" ${isDone})

            if [ ${isDone} -eq 0 ]; then
                /usr/local/bin/scrapy crawl ${spiderName} -a fromCity=${fromCity} -a toCity=${toCity} -a plusDate=${date}
                ret=$?
                if [ ${ret} -eq 0 ]; then
                    jsonFile=${spiderName}.${date}.${fromCity}.${toCity}.json

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
                    echo "Fail(ret=${ret} - scrapy crawl ${spiderName} -a fromCity=${fromCity} -a toCity=${toCity} -a plusDate=${date}"
                    exit 2
                fi
            else
                echo "Skip ${log}"
            fi
        done
    done
done
