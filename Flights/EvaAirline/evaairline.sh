#!/bin/sh

basepath=$(dirname "$0")
cd ${basepath}

fromAreaFile=$1
fromArea=$(basename ${fromAreaFile} | cut -d "." -f1)
if [ ! -s "${fromAreaFile}" ]; then
    echo "Not Found - ${fromAreaFile}"
    exit 1
fi

spiderName=EvaAirline
today=$(date +%Y%m%d)

jobPath=${spiderName}/${today}
mkdir -p ${jobPath}/json

logPath=${spiderName}.${today}.log
touch ${logPath}

for fromCity in $(cat ${fromAreaFile});
do
    for date in $(echo "7,45");
    do
        log=${fromCity}-${date}

        isDone=$(grep "${log}" ${logPath} | wc -l)
        isDone=$(printf "%d" ${isDone})

        if [ ${isDone} -eq 0 ]; then
            dateStart=$(echo ${date} | cut -d "," -f1)
            dateEnd=$(echo ${date} | cut -d "," -f2)

            /usr/local/bin/scrapy crawl ${spiderName} -a fromArea=${fromArea} -a fromCity=${fromCity} -a dateStart=${dateStart} -a dateEnd=${dateEnd}
            ret=$?
            if [ ${ret} -eq 0 ]; then
                jsonFile=${spiderName}.${dateStart}.${fromCity}.json

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
                echo "Fail(ret=${ret} - scrapy crawl ${spiderName} -a fromArea=${fromArea} -a fromCity=${fromCity} -a dateStart=${dateStart} -a dateEnd=${dateEnd})"
                exit 2
            fi
        else
            echo "Skip ${log}"
        fi
    done
done
