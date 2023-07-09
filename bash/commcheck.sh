#!/bin/bash

#refenence link : https://blog.dalso.org/article/bash-%EC%89%98-%EC%8A%A4%ED%81%AC%EB%A6%BD%ED%8A%B8%EB%A1%9C-%EB%84%A4%ED%8A%B8%EC%9B%8C%ED%81%AC-%EC%9E%A5%EC%B9%98%EB%AA%85-ip-mac-%EC%A3%BC%EC%86%8C



#Network Check Logic
######
num_tried=1


DEV=""
IP=""
MAC=""

while [ -z ${IP} ] && [ ${num_tried} -lt 21 ]
do
    DEV_LIST=$(ip route show default | awk '/default/{print $5}')
    DEV_ISEXIST=0
    for ((i=1;i<100;i++)) do
        DEV_ITEM=$(echo $DEV_LIST | awk '{print $'$i'}')

        if [ ${#DEV_ITEM} -eq 0 ]; then
            DEV=${DEV_ITEM}
            DEV_ISEXIST=0
            break
        fi

        if [ ${DEV_ITEM} == "wlan0" ]; then
            DEV=${DEV_ITEM}
            DEV_ISEXIST=1
            break
        fi

    done

    echo -e "\n\n"

    if [ 0 -eq ${DEV_ISEXIST} ]; then
        echo "Network Detection Trial ${num_tried} / 20"
        echo "Network Interface Not Found"
        #CHECK per 3 sec
        num_tried=`expr $num_tried + 1`
        sleep 3
        continue
    else
        echo "Network Detection Trial ${num_tried} / 20"
        echo "Network Interface Found!"
    fi


    IP=$(ip -4 -o addr show ${DEV} | awk '{print $4}')
    IP=$(echo $IP | cut -d '/' -f1)
    if [ ${IP} == "127.0.0.1" ]; then
        echo "IP Address Not Found"
        #CHECK per 3 sec
        num_tried=`expr $num_tried + 1`
        sleep 2
        continue
    fi


    MAC=$(cat /sys/class/net/${DEV}/address)
    if [ -z ${MAC} ]; then
        echo "mac address not found"
        continue
    fi
    
    exit 0
done

exit 1