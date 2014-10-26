#!/bin/sh

path_ticket=/Users/rungchi_chen/Documents/travel/tekcit

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
run ${path_ticket}/Flights/ChinaAirline/chinaairline.sh ${path_ticket}/Flights/ChinaAirline/fromCity.cfg ${path_ticket}/Flights/ChinaAirline &

# 亞洲航空
run ${path_ticket}/Flights/AirAsia/asiaair.sh ${path_ticket}/Flights/AirAsia/fromCity.cfg ${path_ticket}/Flights/AirAsia &

# 酷航
run ${path_ticket}/Flights/Flyscoot/flyscoot.sh ${path_ticket}/Flights/Flyscoot/fromCity.cfg ${path_ticket}/Flights/Flyscoot &

# 捷星航空
run ${path_ticket}/Flights/JetStar/jetstar.sh ${path_ticket}/Flights/JetStar/fromCity.cfg ${path_ticket}/Flights/JetStar &

# CebuPacificAir
run ${path_ticket}/Flights/CebuPacificAir/cebupacificair.sh ${path_ticket}/Flights/CebuPacificAir/fromCity.cfg ${path_ticket}/Flights/CebuPacificAir &

wait
