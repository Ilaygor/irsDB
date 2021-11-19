import zipfile
import os
import datetime
import time
import threading



class Archivator: #дописать логику первого запуска

    def __init__(self, database):
        f = open('log.txt', 'a')
        f.write(str(datetime.datetime.now()) + ' start of work\n')
        self.database = database


    def arch(self, cause): #создание архива с названим текущей даты
        f = open('log.txt', 'a')
        data = datetime.datetime.now()
        f.write(str(data) +' '+ cause + '\n')
        archiv = zipfile.ZipFile('backup/'+data.strftime("%Y_%m_%d_%H%M%S")+'.zip', 'w')
        archiv.write(self.database, compress_type=zipfile.ZIP_DEFLATED)
        archiv.close()


    def getConfig(self):#получение данных из конфига и составление из них словаря
        f = open('config.txt', 'r')
        lines = f.readlines()
        params =[]
        for line in lines:
            params.append(tuple(line.replace('\n','').split(' ')))
        return dict(params)


    def autoarch(self): # проверка параметров автоархивации и архивация при необходимости
        config = self.getConfig()
        deltatime = datetime.timedelta(hours=int(config['periodH']), minutes=int(config['periodM']),
                                   seconds=int(config['periodS']))
        maxArchSize = int(config['sizeparam'])
        f = open('log.txt', 'r')
        lastbackuptime = datetime.datetime.fromisoformat(f.readlines()[-1][:26])
        if datetime.datetime.now() - lastbackuptime > deltatime:
            self.arch("periodic backup")
        elif os.path.getsize(self.database) > maxArchSize:
            self.arch("oversize")



def archivete(archivator):

  threading.Timer(600.0, archivete).start()
  print("Archiv")
  archivator.autoarch()

if __name__ == "__main__":
    #A = Archivator("IRSwelding.db")
    #A.arch('test')
    pass


