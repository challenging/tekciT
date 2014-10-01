#!/bin/sh

basepath=$(dirname "$0")
cd ${basepath}

areaFile=$1
if [ ! -s "${areaFile}" ]; then
    echo "Not Found - ${areaFile}"
    exit 1
fi

spiderName=Peach
today=$(date +%Y%m%d)

jobPath=${spiderName}/${today}
mkdir -p ${jobPath}/json

logPath=${spiderName}.${today}.log
touch ${logPath}

for fromCity in $(echo "TPE" "HKG" "KHH" "ICN" "PUS" "MYJ" "NRT" "MYJ" "FUK" "NGS" "KOJ" "ISG");
do
    for toCity in $(cat ${areaFile});
    do
        for date in $(echo "7,45");
        do
            log=${fromCity}-${toCity}-${date}

            isDone=$(grep "${log}" ${logPath} | wc -l)
            isDone=$(printf "%d" ${isDone})

            if [ ${isDone} -eq 0 ]; then
                dateStart=$(echo ${date} | cut -d "," -f1)
                dateEnd=$(echo ${date} | cut -d "," -f2)

                /usr/local/bin/scrapy crawl ${spiderName} -a fromCity=${fromCity} -a toCity=${toCity} -a dateStart=${dateStart} -a dateEnd=${dateEnd}
                ret=$?
                if [ ${ret} -eq 0 ]; then
                    jsonFile=${spiderName}.${dateStart}.${fromCity}.${toCity}.json

                    if [ -s "${spiderName}.${today}.json" ]; then
                        mv ${spiderName}.${today}.json ${jsonFile}
                        mv ${jsonFile} ${jobPath}/json
                    else
                        echo "Empty Results - ${spiderName}.${today}.json"
                    fi

                    echo "${log}" >> ${logPath}
                    sleep 5
                else
                    echo "Fail(ret=${ret} - scrapy crawl ${spiderName} -a fromCity=${fromCity} -a toCity=${toCity} -a dateStart=${dateStart} -a dateEnd=${dateEnd})"
                    exit 2
                fi
            else
                echo "Skip ${log}"
            fi
        done
    done
done
