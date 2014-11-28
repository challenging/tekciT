#!/bin/sh

action=$1

for flight in $(echo ChinaAirline AirAsia Flyscoot JetStar CebuPacificAir Peach EvaAirline ChinaEastern AirBusan VanillaAir TigerAir CsAir);
do
    python service.py -p ${flight} -a ${action}
    if [ ${action} == "stop" ]; then
        for pid in $(ps aux | grep ${flight} | grep scrapy | awk '{print $2}');
        do
            kill -9 ${pid}
        done
    fi
done
