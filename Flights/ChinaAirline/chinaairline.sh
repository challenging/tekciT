#!/bin/sh

basepath=$(dirname "$0")
echo "Change working directory - ${basepath}"
cd "${basepath}"

areaFile=$1
if [ ! -e "${areaFile}" ]; then
    echo "Not Found ${areaFile}"
    exit 999
fi

spiderName=ChinaAirline
date=$(date +%Y%m%d)

jobPath=${spiderName}/${date}
mkdir -p ${jobPath}/json

logPath=${spiderName}.${date}.log
touch ${logPath}

for country in $(cat "${areaFile}");
do
    isDone=$(grep "${country}" ${logPath} | wc -l)
    isDone=$(printf "%d" ${isDone})

    if [ ${isDone} -eq 0 ]; then
        for plusDate in $(echo "1" "15" "29" "43");
        do
            /usr/local/bin/scrapy crawl ${spiderName} -a toCity=${country} -a fromCity=TPE -a plusDate=${plusDate} -a periodType=0 -s JOBDIR=${jobPath}

            jsonFile=${spiderName}.${date}.${country}.${plusDate}.json
            if [ -s ${jsonFile} ]; then
                jsonFile=${spiderName}.${date}.${country}.${plusDate}.json

                mv ${spiderName}.${date}.json ${jsonFile}
                mv ${jsonFile} ${jobPath}/json
            else
                echo "Empty Results - ${jsonFile}"
                rm -f ${jsonFile}
            fi

            sleep 5
        done

        echo "${country}" >> ${logPath}
    else
        echo "Skip ${country}"
    fi
done
