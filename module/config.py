#!/usr/bin/env python
# -*- coding: utf-8 -*-
# handles general config stuff
import yaml


def read_config(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)
