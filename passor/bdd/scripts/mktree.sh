#!/usr/bin/env bash
mkdir -p testcases
mkdir -p scripts
for x in credit madai contract payment wangxiao zhangwu zhanzhao zhengxin ; do 
	mkdir -p testcases/$x/features
	touch testcases/$x/features/demo.feature
done

