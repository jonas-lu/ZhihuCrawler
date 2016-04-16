#!/bin/bash
if [ $# != 2 ]
then
    echo "Usage: crawler master|slave start|stop"
    exit 1
fi

case $1 in
    "master")
        case $2 in
            "start")
                echo "Starting master..."
                nohup python3 ./src/main.py master >> master.log 2>&1 &
                echo $! > ./run/master.pid
                ;;
            "stop")
                echo "Stoping master..."
                pid=`cat ./run/master.pid`
                kill -SIGTERM ${pid}
                rm -f ./run/master.pid
                echo "Stopped"
                ;;
            *)
                echo "Invalid argument"
                ;;
        esac
        ;;
    "slave")
        case $2 in
            "start")
                echo "Starting slave..."
                nohup python3 ./src/main.py slave >> slave.log 2>&1 &
                echo $! > ./run/slave.pid
                ;;
            "stop")
                echo "Stoping slave..."
                pid=`cat ./run/slave.pid`
                kill -SIGTERM ${pid}
                rm -f ./run/slave.pid
                echo "Stopped"
                ;;
            *)
                echo "Invalid argument"
                ;;
        esac
        ;;
    *)
        echo "Invalid argument"
        ;;
esac