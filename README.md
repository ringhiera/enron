# summarize-enron.py

## Assumption
- The user has basic familiarity with shell, python3, pip, and virtual environments
- The system has python3.5, pip, virtualenv installed

## Preparation (Only the first time)
- Create your python 3 virtual environment (```virtualenv -p /usr/bin/python3.5 env``` works on most systems)
- Activate the environment (```source env/bin/activate ```)
- Install requirements form requirements.txt (```pip install -r requirements.txt```)

## Run
- Activate the environment (as above)
- Run the script as  ```python summarize-enron.py <path-to-input.csv>```
- the files are saved as
- - path-to-input-summary.csv
- - path-to-input-top-sender-sent.png
- - path-to-input-top-sender-received.png

