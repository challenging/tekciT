#!/bin/sh

ws_path=$(dirname $0)

run(){
    local scrapy=$1
    local to=$2

    for city in $(ls ${to}/toCity*.cfg);
    do
        city=$(basename ${city})
        ${scrapy} fromCity.cfg ${city}
    done
}

# 樂桃航空
run ${ws_path}/Peach/peach.sh ${ws_path}/Peach &

# 長榮航空
#run ${ws_path}/EvaAirline/evaairline.sh ${ws_path}/EvaAirline &

# 中國航空
run ${ws_path}/ChinaEastern/chinaeastern.sh ${ws_path}/ChinaEastern &

# AirBusan
run ${ws_path}/AirBusan/airbusan.sh ${ws_path}/AirBusan &

# 香草航空 - VanillaAir
run ${ws_path}/VanillaAir/vanillaair.sh ${ws_path}/VanillaAir &

# 虎航
run ${ws_path}/Flight/TigerAir/tigerair.sh ${ws_path}/TigerAir &

# 南方航空
run ${ws_path}/Flight/CsAir/csair.sh ${ws_path}/CsAir &

wait
