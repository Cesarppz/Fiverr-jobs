import pandas as pd
import argparse
from datetime import date, datetime
import logging
import subprocess

# Fecha de hoy
dia = datetime.now().day
mes = datetime.now().month
hour = datetime.now().hour
minute = datetime.now().minute
sec = datetime.now().second
# Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M')
logger = logging.getLogger('Scarpe-app')

def transform_csv_to_excel(file, list=False):
    if list == False:
        df = pd.read_csv(file)
        df.to_excel(f'results_files/results_{dia}_of_{mes}_{hour}{minute}{sec}.xlsx',index=False)
        logger.info('Datos transformados')
    else:
        box_data_frames = []
        for p in file:
            box_data_frames.append(pd.read_csv(p))

        df = pd.concat(box_data_frames,axis='rows')
        df.to_excel(f'results_files/results_{dia}_of_{mes}_{hour}{minute}{sec}.xlsx',index=False)
        logger.info('Datos transformados')


def move_and_remove(name, category, geo_zone):
    path = f'./{name}'
    logger.info(f'Scraping {name} ...')
    if category != None and geo_zone == None:
        try:
            # print('Category',category)
            subprocess.run(['scrapy','crawl',f'{name}','-a',f'category={category}','--loglevel','INFO'],cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info(f'Scraping {name}')
            try:
                subprocess.run(['mv',f'results_{name}_{dia}_{mes}.csv','../'],cwd=path)
            except FileNotFoundError:
                logger.error('Error al mover el archivo')
        except Exception as e:
            logger.error(f'Error ejecutando el programa {name}')
            
        return f'results_{name}_{dia}_{mes}.csv'
    elif geo_zone != None and category == None:
        try:
            subprocess.run(['scrapy','crawl',f'{name}','-a',f'geo_zone={geo_zone}','--loglevel','INFO'],cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info(f'Scraping {name}')
            try:
                subprocess.run(['mv',f'results_{name}_{dia}_{mes}.csv','../'],cwd=path)
            except FileNotFoundError:
                logger.error('Error al mover el archivo')
        except Exception as e:
            logger.error(f'Error ejecutando el programa {name}')
            
        return f'results_{name}_{dia}_{mes}.csv'
    elif geo_zone == True and category == True:
        try:
            subprocess.run(['scrapy','crawl',f'{name}','-a',f'category={category}','-a',f'geo_zone={geo_zone}','--loglevel','INFO'],cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info(f'Scraping {name}')
            try:
                subprocess.run(['mv',f'results_{name}_{dia}_{mes}.csv','../'],cwd=path)
            except FileNotFoundError:
                logger.error('Error al mover el archivo')
        except Exception as e:
            logger.error(f'Error ejecutando el programa {name}')
            
        return f'results_{name}_{dia}_{mes}.csv'
    else:
        try:
            subprocess.run(['scrapy','crawl',f'{name}','--loglevel','INFO'],cwd=path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info(f'Scraping {name}')
            try:
                subprocess.run(['mv',f'results_{name}_{dia}_{mes}.csv','../'],cwd=path)
            except FileNotFoundError:
                logger.error('Error al mover el archivo')
        except Exception as e:
            logger.warning(f'Error ejecutando el programa {name}')
            
    return f'results_{name}_{dia}_{mes}.csv'


def run_multiple_program(names,category,geo_zone,one_category=False,one_geo_zone=False):
    if category == None and geo_zone == None:
        box_files = []                
        for name in names:
           # print('Names',name)
            file = move_and_remove(name, category, geo_zone)
            box_files.append(file)
        transform_csv_to_excel(box_files,list=True)
    
    elif category != None and geo_zone == None:
        if len(category) == len(names):  # Cada programa tiene su categoria
            box_files = []                
            for idx, name in enumerate(names):
                print(category[idx])
                file = move_and_remove(name, category[idx], geo_zone)
                box_files.append(file)
            transform_csv_to_excel(box_files,list=True)
        
            transform_csv_to_excel(box_files,list=True)
        elif len(category) == 1:                               #Hay una sola categoria para todos
            box_files = []                
            for idx, name in enumerate(names):
                file = move_and_remove(name, category[0], geo_zone)
                box_files.append(file)
            transform_csv_to_excel(box_files,list=True)
    
    elif category == None and geo_zone != None:
        if len(geo_zone) == len(names):  # Cada programa tiene su geo_zone
            box_files = []                
            for idx, name in enumerate(names):
                file = move_and_remove(name, category, geo_zone[idx])
                box_files.append(file)
            transform_csv_to_excel(box_files,list=True)
        elif len(geo_zone) == 1:                               #Hay una sola geo_zone para todos
            box_files = []                
            for idx, name in enumerate(names):
                file = move_and_remove(name, category, geo_zone[0])
                box_files.append(file)
            transform_csv_to_excel(box_files)

    elif category != None and geo_zone != None:
        if len(geo_zone) == len(names) and len(category) == len(names):  # Cada programa tiene su geo_zone y su catgeort
            box_files = []                
            for idx, name in enumerate(names):
                category_idx = category[idx] 
                if category_idx.lower() == 'none':
                    category_idx = None
                geo_zone_idx = geo_zone[idx]
                if geo_zone_idx.lower() == 'none':
                    geo_zone_idx = None
                
                file = move_and_remove(name, category_idx, geo_zone_idx)
                box_files.append(file)
            transform_csv_to_excel(box_files,list=True)
        
        elif len(geo_zone) == 1 and len(category) == 1:                               #Hay una sola geo_zone para todos y una sola categoria
            box_files = []                
            for idx, name in enumerate(names):
                file = move_and_remove(name, category[0], geo_zone[0])
                box_files.append(file)
            transform_csv_to_excel(box_files,list=True)
        
def main(args):
    if args.file:
        if type(args.file) == list:
            transform_csv_to_excel(args.file,list=True)
        else:
            transform_csv_to_excel(args.file)

    elif args.run:
        if len(args.run) >= 2:

            run_multiple_program(args.run, args.category,args.geo_zone)

        else:
            try:
                category = args.category[0]
            except TypeError:
                category = None 
            try:
                geo_zone = args.geo_zone[0]
            except TypeError:
                geo_zone = None

            file = move_and_remove(args.run[0], category, geo_zone)
            #print(f'file: {file}')
            transform_csv_to_excel(file)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file','-f',help='Introduzca la ruta del archivo que quiere convertir a csv',nargs='?',action='append')
    parser.add_argument('--run','-r',help='introduza el nomnre o nombres de los programas que quiere correr',nargs='?', action='append',choices=['escorts_mexico', 'geisha_academy', 'gemidos', 'selfiescorts', 'la_boutique', 'putas_vip_mexico',  'seductora', 'dessires', 'scorts_natural', 'mileroticos', 'mil_avisos', 'chicas_y_escorts', 'top_models_mx', 'evas', 'zonadivas' , 'mundosexanuncio', 'bombachitas_regias', 'skokka', 'divas_mexico', 'angeles_mex', 'encuentro_chicas', 'atlas_escorts', 'sustitutas', 'loguo_vip', 'sensualonas', 'adultguia'])
    parser.add_argument('--category','-c',help='Introduzca la categoria que quiere buscar',nargs='?', action='append')
    parser.add_argument('--geo_zone','-g',help='Introduzca la zona geografica que quiere buscar', nargs='?', action='append')
    args = parser.parse_args()
    #print(args.run)
    main(args)
