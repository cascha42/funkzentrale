#!/usr/bin/env bash

sudo systemctl restart audioplayer
journalctl -xefu audioplayer
