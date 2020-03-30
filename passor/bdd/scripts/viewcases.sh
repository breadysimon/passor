#!/usr/bin/env bash
docker run -v $PWD/../testcases:/input -v $PWD/..:/output case-viewer
open $PWD/../html/index.html
