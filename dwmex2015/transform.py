import pandas as pd
import argparse
from datetime import datetime
import logging
import subprocess

# Fecha de hoy
dia = datetime.now().day
mes = datetime.now().month
# Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M')
logger = logging.getLogger('Scarpe-app')

def transform_csv_to_excel(file, list=False):
    if list == False:
        df = pd.read_csv(file)
        df.to_excel(f'results_files/results_{dia}_of_{mes}.xlsx',index=False)
        logger.info('Datos transformados')
    else:
        box_data_frames = []
        for p in file:
            box_data_frames.append(pd.read_csv(p))

        df = pd.concat(box_data_frames,axis='columns')
        df.to_excel(f'results_files/results_{dia}_of_{mes}.xlsx',index=False)
        logger.info('Datos transformados')


def move_and_remove(name):
    path = f'./{name}'
    try:
        subprocess.run(['scrapy','crawl',f'{name}','--loglevel','INFO'],cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info(f'Scraping {name}')
        try:
            subprocess.run(['mv',f'results_{name}_{dia}_{mes}.csv','../'],cwd=path)
        except FileNotFoundError:
            logger.error('Error al mover el archivo')
    except Exception as e:
        logger.error(f'Error ejecutando el programa {name}')
        
    return f'results_{name}_{dia}_{mes}.csv'


def main(args):
    if args.file:
        if type(args.file) == list:
            transform_csv_to_excel(args.file,list=True)
        else:
            transform_csv_to_excel(args.file)
    
    elif args.run:
        if type(args.run) == list:
            box_files = []
            for name in args.run:
                file = move_and_remove(name)
                box_files.append(file)
            transform_csv_to_excel(box_files,list=True)
        else:
            file = move_and_remove(args.run)
            transform_csv_to_excel(file)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file','-f',help='Introduzca la ruta del archivo que quiere convertir a csv',nargs='?',action='append')
    parser.add_argument('--run','-r',help='introduza el nomnre o nombres de los programas que quiere correr',nargs='?', action='append')
    args = parser.parse_args()
    main(args)
