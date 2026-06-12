#!/bin/bash
set -ex

project=

$project/.venv/bin/python $project/npi-api.py s -g ИСПа -f F -c 3 $@
