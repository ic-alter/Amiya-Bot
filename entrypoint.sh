#!/bin/bash

BOT_FOLDER=/amiyabot

# step 0: 备份config文件夹
if [ -d "$BOT_FOLDER/config/" ]; then
    cp -r $BOT_FOLDER/config $BOT_FOLDER/config.bak
fi

# step 1: 解压/覆盖bot文件
if [ -f "amiyabot.tar.gz" ]; then
    tar -zxvf amiyabot.tar.gz -C $BOT_FOLDER
    rm amiyabot.tar.gz
fi

# step 2: 判断是否首次运行
if [ ! -f "$BOT_FOLDER/first_run" ]; then
    cd $BOT_FOLDER
    python entrypoint.py
else
    cp -r $BOT_FOLDER/config.bak $BOT_FOLDER/config
fi

# step 3: 启动bot
cd $BOT_FOLDER
python amiya.py