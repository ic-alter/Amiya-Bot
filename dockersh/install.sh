#!/bin/bash

# step 1: 准备docker环境
if [ -x "$(command -v docker)" ]; then
    echo "Docker 已安装"
else
    echo "Docker 未安装, 开始安装..."
    sudo apt-get update
    sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    sudo apt-get update
    sudo apt-get install -y docker-ce
fi

# step 2: 收集环境变量
while true; do
    echo -n "是否启用mysql? [y/n] (默认: 使用sqlite): "
    read mysql_enable
    if [ "$mysql_enable" ]; then 
        if [ "$mysql_enable" = "y" ] || [ "$mysql_enable" = "Y" ]; then
            mysql_enable=true
            echo -n "请输入mysql主机地址 (默认: 127.0.0.1): "
            read mysql_host
            echo -n "请输入mysql端口 (默认: 3306): "
            read mysql_port
            echo -n "请输入mysql用户名: "
            read mysql_user
            echo -n "请输入mysql密码: "
            read mysql_password
            break
        elif [ "$mysql_enable" = "n" ] || [ "$mysql_enable" = "N" ]; then
            mysql_enable=false
            break
        else
            echo "请输入y或n"
            continue
        fi
    else
        echo "请输入y或n"
        continue
    fi
    done
        
while true; do
    echo -n "是否修改前缀? [y/n] (默认: 兔兔): "
    read prefix_enable
    if [ "$prefix_enable" ]; then
        if [ "$prefix_enable" = "y" ] || [ "$prefix_enable" = "Y" ]; then
            echo -n "请输入前缀, 用','分隔: "
            read prefix
            # 将前缀转换为python列表
            prefix="[\"$(echo $prefix | sed 's/,/\",\"/g')\"]"
            break
        elif [ "$prefix_enable" = "n" ] || [ "$prefix_enable" = "N" ]; then
            break
        else
            echo "请输入y或n"
            continue
        fi
    else
        echo "请输入y或n"
        continue
    fi
    done

while true; do
    echo -n "是否修改AuthKey? [y/n] (默认: 无): "
    read auth_enable
    if [ "$auth_enable" ]; then
        if [ "$auth_enable" = "y" ] || [ "$auth_enable" = "Y" ]; then
            echo -n "请输入AuthKey: "
            read auth
            break
        elif [ "$auth_enable" = "n" ] || [ "$auth_enable" = "N" ]; then
            break
        else
            echo "请输入y或n"
            continue
        fi
    else
        echo "请输入y或n"
        continue
    fi
    done

while true; do
    echo -n "是否修改端口? [y/n] (默认: 8088): "
    read port_enable
    if [ "$port_enable" ]; then
        if [ "$port_enable" = "y" ] || [ "$port_enable" = "Y" ]; then
            echo -n "请输入端口: "
            read port
            break
        elif [ "$port_enable" = "n" ] || [ "$port_enable" = "N" ]; then
            port=8088
            break
        else
            echo "请输入y或n"
            continue
        fi
    else
        echo "请输入y或n"
        continue
    fi
    done

# # step 3: 运行docker

while true; do
    echo -n "是否将amiyabot挂载到本地? [y/n] (默认挂载到amiyabot存储卷): "
    read mount_enable
    if [ "$mount_enable" ]; then
        if [ "$mount_enable" = "y" ] || [ "$mount_enable" = "Y" ]; then
            echo -n "请输入挂载路径 (默认: $HOME/amiyabot): "
            read mount_path
            if [ ! "$mount_path" ]; then
                mount_path="$HOME/amiyabot"
            fi
            break
        elif [ "$mount_enable" = "n" ] || [ "$mount_enable" = "N" ]; then
            break
        else
            echo "请输入y或n"
            continue
        fi
    else
        echo "请输入y或n"
        continue
    fi
    done

echo -n "请输入容器名称 (默认: amiyabot): "
read container_name
if [ ! "$container_name" ]; then
    container_name="amiyabot"
fi

command="sudo docker run -d --name $container_name"
if [ "$mysql_enable" = true ]; then
    command="$command -e ENABLE_MYSQL=true -e MYSQL_HOST=$mysql_host -e MYSQL_PORT=$mysql_port -e MYSQL_USER=$mysql_user -e MYSQL_PASSWORD=$mysql_password"
fi
if [ "$prefix" ]; then
    command="$command -e PREFIX=\"$prefix\""
fi
if [ "$auth" ]; then
    command="$command -e AUTH=$auth"
fi
if [ "$port" ]; then
    command="$command -p $port:8088"
fi
if [ "$mount_path" ]; then
    command="$command -v $mount_path:/amiyabot"
else
    command="$command -v amiyabot:/amiyabot"
fi
command="$command amiyabot/amiyabot:latest"

while true; do
    echo "即将运行命令: $command, 是否继续? [y/n] (默认: n)"
    read confirm
    if [ "$confirm" ]; then
        if [ "$confirm" = "y" ]; then
            sudo docker pull amiyabot/amiyabot:latest
            eval $command
            echo "服务已启动, 控制台地址: http://<本机ip>:$port"
            break
        elif [ "$confirm" = "n" ]; then
            echo "已取消"
            break
        else
            echo "请输入y或n"
            continue
        fi
    else
        echo "请输入y或n"
        continue
    fi
    done