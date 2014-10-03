#!/bin/sh

basepath=$(dirname "$0")
cd ${basepath}

areaFile=$1
if [ ! -s "${areaFile}" ]; then
    echo "Not Found - ${areaFile}"
    exit 1
fi

spiderName=AirAsia
today=$(date +%Y%m%d)

jobPath=${spiderName}/${today}
mkdir -p ${jobPath}/json

logPath=${spiderName}.${today}.log
touch ${logPath}

for fromCity in $(echo "TPE");
do
    for toCity in $(cat ${areaFile});
    do
        #for date in $(echo "7" "14" "21" "28" "35");
        for date in $(echo "21" "49");
        do
            log=${fromCity}-${toCity}-${date}

            isDone=$(grep "${log}" ${logPath} | wc -l)
            isDone=$(printf "%d" ${isDone})

            fromCity=$(echo ${fromCity} | sed 's/-/ /g')
            toCity=$(echo ${toCity} | sed 's/-/ /g')

            if [ ${isDone} -eq 0 ]; then
                /usr/local/bin/scrapy crawl ${spiderName} -a fromCity="${fromCity}" -a toCity="${toCity}" -a plusDate=${date}
                ret=$?
                if [ ${ret} -eq 0 ]; then
                    jsonFile="${spiderName}.${date}.${fromCity}.${toCity}.json"

                    if [ -s "${spiderName}.${today}.json" ]; then
                        mv "${spiderName}.${today}.json" "${jsonFile}"
                        mv "${jsonFile}" ${jobPath}/json
                    else
                        echo "Empty Results - ${spiderName}.${today}.json" >> ${logPath}
                        rm "${spiderName}.${today}.json"
                    fi

                    echo "${log}" >> ${logPath}
                    sleep 5
                else
                    echo "Fail(ret=${ret} - scrapy crawl ${spiderName} -a fromCity=${fromCity} -a toCity=${toCity} -a plusDate=${date})"
                    rm "${spiderName}.${today}.json"
                fi
            else
                echo "Skip ${log}"
            fi
        done
    done
done
