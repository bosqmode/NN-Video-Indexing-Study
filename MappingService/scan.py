import os

SEARCH_ROOT = '../data'

for root, dirs, files in os.walk(SEARCH_ROOT):
    for name in files:
        print(name)