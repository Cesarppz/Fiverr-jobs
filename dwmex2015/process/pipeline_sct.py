#!/home/cesarppz/anaconda3/envs/ws/bin/python3
import subprocess
import logging
import datetime as dt
import os
import sys
import argparse
import re

from read_yaml import  read_yaml, write_yaml
from datetime import datetime
from cancat import concat_dataframes

# Fecha de hoy
dia = datetime.now().day
mes = datetime.now().month
# Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M')
logger = logging.getLogger('Scarpe-app')


def main(args):
    if args.all == 'true':
        run_scrapy(who='all')
    else:
        read_yaml()
        run_scrapy()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--all','-a',type=str,help='Hacer scrape de todos los sitios',default='true',choices=['true','false'],nargs='?')
    parser.add_argument('--dir_path','-dp',type=str,help='Proporcione la dirección de la carpeta de destino',nargs='?')
    args = parser.parse_args()
    main(args)