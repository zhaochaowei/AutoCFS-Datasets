#!/bin/bash
mapfile -t files < <(sed -n "$1,$2p" a.log)
vim -O "${files[@]}"
