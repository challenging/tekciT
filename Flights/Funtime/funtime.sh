#!/bin/sh

basepath=.

spiderName=funtime
date=$(date +%Y%m%d)

jobPath=${basepath}/${spiderName}/${date}
mkdir -p ${jobPath}/json

logPath=${spiderName}.${date}.log
touch ${logPath}

for country in $(echo 'korea' 'russia' 'switzerland' 'holland' 'australia' 'newzealand' 'england' 'hungary' 'denmark' 'sweden' 'czech' 'norway' 'europe' 'ireland' 'portugal' 'france' 'finland' 'spanish' 'austria' 'belgium' 'greece' 'italy' 'japan' 'germany');
do
    isDone=$(grep "${country}" ${logPath} | wc -l)
    isDone=$(printf "%d" ${isDone})

    if [ ${isDone} -eq 0 ]; then
        /usr/local/bin/scrapy crawl ${spiderName} -a country=${country} -s JOBDIR=${jobPath}

        ret=$?
        if [ ${ret} -eq 0 ]; then
            echo "${country}" >> ${logPath}

            mv ${spiderName}.${date}.json ${spiderName}.${date}.${country}.json
            mv ${spiderName}.${date}.${country}.json ${jobPath}/json
 
            rm -fR jobPath
        else
            echo "Fail(ret=${ret} - scrapy crawl ${spiderName} -a country=${country} -s JOBDIR=${jobPath})"
            exit 999
        fi
    else
        echo "Skip ${country}"
    fi
done
