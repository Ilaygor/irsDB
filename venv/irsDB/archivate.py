import zipfile
import os
import datetime
import time
import threading

print("import archivate")

class Archivator: #дописать логику первого запуска

    def __init__(self, database):
        f = open('log.txt', 'a')
        f.write(str(datetime.datetime.now()) + ' start of work\n')
        self.database = database

    # создание архива с названим текущей даты
    def arch(self, cause):
        f = open('log.txt', 'a')
        data = datetime.datetime.now()
        f.write(str(data) +' '+ cause + '\n')
        archiv = zipfile.ZipFile('backup/'+data.strftime("%Y_%m_%d_%H%M%S")+'.zip', 'w')
        archiv.write(self.database, compress_type=zipfile.ZIP_DEFLATED)
        archiv.close()

    # получение данных из конфига и составление из них словаря
    def getConfig(self):
        f = open('config.txt', 'r')
        lines = f.readlines()
        params =[]
        for line in lines:
            params.append(tuple(line.replace('\n','').split(' ')))
        return dict(params)

    # проверка параметров автоархивации и архивация при необходимости
    def autoarch(self):
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

    #запуск васинхронного архивирования
    def archivete(self):
      threading.Timer(600.0, archivete).start()
      print("Archiv")
      self.autoarch()

    def dearchivete(self):
        return 0

if __name__ == "__main__":
    #A = Archivator("IRSwelding.db")
    #A.arch('test')
    pass


