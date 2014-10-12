#!/bin/sh

SCRAPY=/usr/local/bin/scrapy
SCRAPY_OPTS=crawl

spiderName=
today=
jobPath=
logPath=

isExists(){
    local file=$1
    if [ ! -s "${file}" ]; then
        echo "Not Found ${file} so Terminate!"
        exit 1
    fi
}

init(){
    local fromCityFile=$2
    local toCityFile=$3

    isExists ${fromCityFile} ${toCityFile}

    today=$(date +%Y%m%d)

    jobPath=${spiderName}/${today}
    mkdir -p ${jobPath}/json

    logPath=${spiderName}.${today}.log
    touch ${logPath}
}

isSkip(){
    local log=$1

    isDone=$(grep "${log}" ${logPath} | wc -l)
    isDone=$(printf "%d" ${isDone})

    echo ${isDone}
}

success(){
    local date=$1
    local fromCity=$2
    local toCity=$3
    local log=$4

    jsonFile="${spiderName}.${date}.${fromCity}.${toCity}.json"

    if [ -s "${spiderName}.${today}.json" ]; then
        mv "${spiderName}.${today}.json" "${jsonFile}"
        mv "${jsonFile}" ${jobPath}/json
    else
        echo "Empty Results - ${spiderName}.${today}.json" >> ${logPath}
        rm "${spiderName}.${today}.json"
    fi

    echo "${log}" >> ${logPath}
}

fail(){
    local ret=$1
    local cmd=$2

    echo "Fail(ret=${ret} - ${cmd})"
    rm "${spiderName}.${today}.json"
}
