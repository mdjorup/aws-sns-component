#!/bin/bash
./scripts/activate.ps1
mkdir shared
Copy-Item requirements.txt shared/requirements.txt
pip install -r shared/requirements.txt -t shared/python --upgrade