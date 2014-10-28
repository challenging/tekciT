#!/bin/sh

ws_path=$(dirname $0)

run(){
    local scrapy=$1
    local from=$2
    local to=$3

    for city in $(ls ${to}/toCity*.cfg);
    do
        echo ${scrapy} ${from} ${city}
    done
}

# 樂桃航空
run ${ws_path}/Peach/peach.sh ${ws_path}/Peach/fromCity.cfg ${ws_path}/Peach &

# 長榮航空
run ${ws_path}/EvaAirline/evaairline.sh ${ws_path}/EvaAirline/fromCity.cfg ${ws_path}/EvaAirline &

# 中國航空
run ${ws_path}/ChinaEastern/chinaeastern.sh ${ws_path}/ChinaEastern/fromCity.cfg ${ws_path}/ChinaEastern &

# AirBusan
run ${ws_path}/AirBusan/airbusan.sh ${ws_path}/AirBusan/fromCity.cfg ${ws_path}/AirBusan &

# 香草航空 - VanillaAir
run ${ws_path}/VanillaAir/vanillaair.sh ${ws_path}/VanillaAir/fromCity.cfg ${ws_path}/VanillaAir &

# 虎航
run ${ws_path}/Flight/TigerAir/tigerair.sh ${ws_path}/TigerAir/fromCity.cfg ${ws_path}/TigerAir &

# 南方航空
run ${ws_path}/Flight/CsAir/csair.sh ${ws_path}/CsAir/fromCity.cfg ${ws_path}/CsAir &

wait
