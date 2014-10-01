#!/bin/sh

# China Airline
/data/tickets/Flights/ChinaAirline/chinaairline.sh /data/tickets/Flights/ChinaAirline/asis.cfg
/data/tickets/Flights/ChinaAirline/chinaairline.sh /data/tickets/Flights/ChinaAirline/europe.cfg
/data/tickets/Flights/ChinaAirline/chinaairline.sh /data/tickets/Flights/ChinaAirline/america.cfg

# 酷航
/data/tickets/Flights/Flyscoot/flyscoot.sh /data/tickets/Flights/Flyscoot/origin.cfg /data/tickets/Flights/Flyscoot/destination.cfg &

# 捷星航空
/data/tickets/Flights/JetStar/jetstar.sh /data/tickets/Flights/JetStar/destination.cfg

# 長榮航空
/data/tickets/Flights/EvaAirline/evaairline.sh /data/tickets/Flights/EvaAirline/asis.cfg &
/data/tickets/Flights/EvaAirline/evaairline.sh /data/tickets/Flights/EvaAirline/america.cfg
/data/tickets/Flights/EvaAirline/evaairline.sh /data/tickets/Flights/EvaAirline/oceanian.cfg
/data/tickets/Flights/EvaAirline/evaairline.sh /data/tickets/Flights/EvaAirline/europe.cfg
/data/tickets/Flights/EvaAirline/evaairline.sh /data/tickets/Flights/EvaAirline/china.cfg &

# 虎航
00 04 * * * /data/tickets/Flights/TigerAir/tigerair.sh /data/tickets/Flights/TigerAir/fromCity.cfg /data/tickets/Flights/TigerAir/toCity.cfg

wait

# 樂桃航空
/data/tickets/Flights/Peach/peach.sh /data/tickets/Flights/Peach/asis.cfg &

# 香草航空
/data/tickets/Flights/VanillaAir/vanillaair.sh /data/tickets/Flights/VanillaAir/origin.cfg /data/tickets/Flights/VanillaAir/destination.cfg &

# 中國南方航空
/data/tickets/Flights/Csair/csair.sh /data/tickets/Flights/Csair/china.cfg /data/tickets/Flights/Csair/foreign.cfg

# 中國東方航空
/data/tickets/Flights/ChinaEastern/chinaeastern.sh /data/tickets/Flights/ChinaEastern/fromCity.cfg /data/tickets/Flights/ChinaEastern/asis.cfg
/data/tickets/Flights/ChinaEastern/chinaeastern.sh /data/tickets/Flights/ChinaEastern/fromCity.cfg /data/tickets/Flights/ChinaEastern/america.cfg
/data/tickets/Flights/ChinaEastern/chinaeastern.sh /data/tickets/Flights/ChinaEastern/fromCity.cfg /data/tickets/Flights/ChinaEastern/europe.cfg
/data/tickets/Flights/ChinaEastern/chinaeastern.sh /data/tickets/Flights/ChinaEastern/fromCity.cfg /data/tickets/Flights/ChinaEastern/oceanian.cfg
