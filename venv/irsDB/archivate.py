# Класс для архивации и работы с бд в архивированном состоянии
import zipfile
import os
import datetime
import time
import threading

print("import archivate")

class Archivator: #дописать логику первого запуска

    def __init__(self, database):
        self.database = database
        f = open('log.txt', 'a')
        size = os.path.getsize(self.database) // 1000000
        f.write(str(datetime.datetime.now()) + '|' + str(size) + '|start of work\n')

    # создание архива с названим текущей даты
    def arch(self, cause, adress):
        f = open('log.txt', 'a')
        data = datetime.datetime.now()
        size = os.path.getsize(self.database)//1000000
        f.write(str(data) +'|'+str(size)+'|'+ cause + '\n')
        try:
            archiv = zipfile.ZipFile(adress+'/'+data.strftime("%Y_%m_%d_%H%M%S")+'.zip', 'w')
        except:
            os.mkdir(adress)
            archiv = zipfile.ZipFile(adress + '/' + data.strftime("%Y_%m_%d_%H%M%S") + '.zip', 'w')
        archiv.write(self.database, compress_type=zipfile.ZIP_DEFLATED)
        archiv.close()

    # Сохранить текущую БД как архив с именем
    def saveAs(self, DB, saveAdress):
        print(DB,saveAdress)
        archiv = zipfile.ZipFile(saveAdress, 'w')
        archiv.write(DB, compress_type=zipfile.ZIP_DEFLATED)
        archiv.close()

    # получение данных из конфига и составление из них словаря
    def getConfig(self):
        f = open('config.txt', 'r')
        lines = f.readlines()
        params =[]
        for line in lines:
            params.append(tuple(line.replace('\n','').split('|')))
        return dict(params)

    # сохранение настроек автоархивации
    def setConfig(self, adress, hours, minuts, seconds, size):
        f = open('config.txt', 'w')
        f.write('saveAdress|' + adress + '\n')
        f.write('periodH|' + hours + '\n')
        f.write('periodM|' + minuts + '\n')
        f.write('periodS|' + seconds + '\n')
        f.write('sizeparam|' + size + '\n')
        
    # проверка параметров автоархивации и архивация при необходимости
    def autoarch(self):
        config = self.getConfig()
        deltatime = datetime.timedelta(hours=int(config['periodH']), minutes=int(config['periodM']),
                                   seconds=int(config['periodS']))
        archSize = int(config['sizeparam'])
        f = open('log.txt', 'r')
        lastArchData = f.readlines()[-1].split('|')
        lastbackuptime = datetime.datetime.fromisoformat(lastArchData[0])
        print("autoArch",lastbackuptime,int(lastArchData[1]))
        if datetime.datetime.now() - lastbackuptime > deltatime:
            self.arch("periodic backup",config["saveAdress"])
        elif (os.path.getsize(self.database)//1000000)//archSize != int(lastArchData[1])//archSize:
            self.arch("oversize",config["saveAdress"])

    #запуск асинхронного архивирования
    def asincArch(self):
      self.timer = threading.Timer(600.0, self.asincArch)
      self.timer.start()
      print("Archiv")
      self.autoarch()

    def deactivate(self):
        self.timer.cancel()

if __name__ == "__main__":
    #A = Archivator("IRSwelding.db")
    #A.arch('test')
    pass


