# Wikipedia-Map

Scraping Wikipedia in order to create a map of the concepts around a base word (in French), using Gephi, an open source graph visualization platform.
Below is an exemple of a map we can obtain using the base word 'Ampoule':

![alt text](https://github.com/killian31/Wikipedia-Map/raw/main/Ampoule_gephi.png)

## Installation
First, clone this repo 
```bash
git clone https://github.com/killian31/Wikipedia-Map.git
```
Then, install the dependencies
```bash
pip install -r requirements.txt
```

## Usage
To start the program, run 
```bash
python3 wikiscrap.py
```
You will then be prompted to choose the desired language between English (en) and French (fr), before being prompted what is the central topic to start scraping Wikipedia from.
