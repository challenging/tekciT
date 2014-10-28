#!/bin/sh

path_ticket=$(dirname $0)

run(){
    local scrapy=$1
    local from=$2
    local to=$3

    for city in $(ls ${to}/toCity*cfg);
    do
        echo ${scrapy} ${from} ${city}
    done
}

# China Airline
run ${path_ticket}/ChinaAirline/chinaairline.sh ${path_ticket}/ChinaAirline/fromCity.cfg ${path_ticket}/ChinaAirline &

# 亞洲航空
run ${path_ticket}/AirAsia/asiaair.sh ${path_ticket}/AirAsia/fromCity.cfg ${path_ticket}/AirAsia &

# 酷航
run ${path_ticket}/Flyscoot/flyscoot.sh ${path_ticket}/Flyscoot/fromCity.cfg ${path_ticket}/Flyscoot &

# 捷星航空
run ${path_ticket}/JetStar/jetstar.sh ${path_ticket}/JetStar/fromCity.cfg ${path_ticket}/JetStar &

# CebuPacificAir
run ${path_ticket}/CebuPacificAir/cebupacificair.sh ${path_ticket}/CebuPacificAir/fromCity.cfg ${path_ticket}/CebuPacificAir &

wait
