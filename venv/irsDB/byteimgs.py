import struct

print("import byteimgs")

def unzip(c):
    print("unzip")
    par = struct.unpack('%si' % (c[0]+1), c[:4*(c[0]+1)])
    imgs = []
    start = 4*(c[0]+1)
    for img in par[1:]:
        imgs.append(c[start:start+img])
        start += img
    return imgs

def add(c, b):
    par = list(struct.unpack('%si' % (c[0] + 1), c[:4 * (c[0] + 1)]))
    data = c[4 * (c[0] + 1):] + b
    par[0]+=1
    par.append(len(b))
    print(par, data)
    buf = struct.pack('%si' % len(par), *par)
    return buf + data

def dell(c, i):
    par = list(struct.unpack('%si' % (c[0] + 1), c[:4 * (c[0] + 1)]))
    startDell = sum(par[1:1+i])
    imgLen = par.pop(i + 1)
    data = c[4 * (c[0] + 1):]
    newData = data[:startDell] + data[startDell+imgLen:]
    par[0] -= 1
    print(par, newData)
    buf = struct.pack('%si' % len(par), *par)
    return buf + newData