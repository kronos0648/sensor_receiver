#!/bin/bash
num_tried=1
DEV=""
IP=""
MAC=""

#네트워크 검사 최대 20회까지 시행
while [ -z ${IP} ] && [ ${num_tried} -lt 21 ]
do
    #네트워크 인터페이스 탐지
    DEV_LIST=$(ip route show default | awk '/default/{print $5}')
    DEV_ISEXIST=0
    for ((i=1;i<100;i++)) do
        DEV_ITEM=$(echo $DEV_LIST | awk '{print $'$i'}')

        #감지된 네트워크 인터페이스가 없을 때
        if [ ${#DEV_ITEM} -eq 0 ]; then
            DEV=${DEV_ITEM}
            DEV_ISEXIST=0
            break
        fi

        #감지된 네트워크 인터페이스가 무선 랜일 때
        if [ ${DEV_ITEM} == "wlan0" ]; then
            DEV=${DEV_ITEM}
            DEV_ISEXIST=1
            break
        fi

    done

    echo -e "\n\n"

    #감지된 네트워크 인터페이스가 없을 때
    if [ 0 -eq ${DEV_ISEXIST} ]; then
        echo "Network Detection Trial ${num_tried} / 20"
        echo "Network Interface Not Found"
        #시행 횟수를 늘려가며 3초마다 탐지 반복
        num_tried=`expr $num_tried + 1`
        sleep 3
        continue
    else
        echo "Network Detection Trial ${num_tried} / 20"
        echo "Network Interface Found!"
    fi

    #IP 주소 탐지
    IP=$(ip -4 -o addr show ${DEV} | awk '{print $4}')
    IP=$(echo $IP | cut -d '/' -f1)
    # 할당된 IP가 아닌 loopback IP일 경우 => IP 할당 안 된 상태
    if [ ${IP} == "127.0.0.1" ]; then
        echo "IP Address Not Found"
        #CHECK per 3 sec
        num_tried=`expr $num_tried + 1`
        sleep 2
        continue
    fi

    #MAC Address 할당 여부 검사
    MAC=$(cat /sys/class/net/${DEV}/address)
    if [ -z ${MAC} ]; then
        echo "mac address not found"
        continue
    fi
    exit 0
done

exit 1