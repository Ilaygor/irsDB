from mainWinFunc.models import *
import struct
from playhouse.migrate import *
if __name__ == "__main__":
    det = Detail.get(Detail.detailName == "Штуцер")
    print(det.id)


