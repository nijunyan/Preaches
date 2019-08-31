import os
import urllib.request
import re
import threading
from time import ctime, sleep
from string import digits
import wget

def genFileList(decoding = None, gen=False):
    if not gen:
        file = open('PreachesList.txt', 'r', encoding='utf-8')
        content = file.readlines()
        urlList = []
        for i in range(len(content)):
            urlList.append(content[i].split())
        return urlList

    url = 'https://www.fuyin.tv/content/'
    if not decoding:
        decoding = 'gbk'
    req = urllib.request.urlopen(url)
    body = req.read().decode(decoding)
    rule = '<a href=\"/content/view/movid/.*\"'
    rule = re.compile(rule)
    links = rule.findall(body)
    urlDic = {}
    urlList = []
    lines = []
    for link in links:
        rule = '\/.*\/'
        rule = re.compile(rule)
        a_link = rule.findall(link)[0]
        # print(a_link)
        title = link[link.find('title')+7:-1]
        # print(title)
        urlDic[title] = a_link
        urlList.append([title, a_link])
        line = [title, a_link]
        lines.append(line)

    tmpLines = []
    for line in lines:
        flag = False
        for tmpLine in tmpLines:
            if tmpLine[0] == line[0]:
                flag = True
        if flag == True:
            continue
        tmpLines.append(line)

    lines = ''
    for l in tmpLines:
        line = ' '.join(l) + '\n'
        lines += line

    if gen:
        print(os.getcwd())
        file = open('PreachesList.txt', 'w', encoding='utf-8')
        file.write(lines)
        file.close()
    return urlList

def download(seriesPairs, root):
    if not seriesPairs[1]:
        return
    print('start loop',seriesPairs[1], 'at :', ctime())

    file = seriesPairs[1] + '.mp3'
    try:
        wget.download(seriesPairs[0], out=file)
    except:
        print(seriesPairs[1] + ' failed')
    # http://mp3.downs.cnfuyin.com/cdn/newmovall-mp3/06%25B8%25A3%25D2%25F4%25D6%25A4%25B5%25C0%252F%25C4%25C1%25CA%25A6%25BD%25B2%25B5%25C0%252Fl%25C1%25F5%25CD%25AE%252FMP4%252F%25C9%25F1%25B5%25C4%25B9%25FA%25BD%25FC%25C1%25CB%252F04%25D7%25DF%25B9%25FD%25C8%25A5%25B5%25C4%25B6%25F7%25B8%25E0.mp3
    print('done', seriesPairs[1], 'at:', ctime())

class MyThread(object):
    def __init__(self, func, args, name=''):
        self.name = name
        self.func = func
        self.args = args

    def __call__(self):
        self.func(*self.args)

def startSeries(root, seriesPairs):
    if not os.path.exists(root):
        try:
            os.mkdir(root)
        except:
            pass
    os.chdir(root)

    filelist = os.listdir(os.getcwd())

    for i in filelist:
        if os.path.isfile(i):
            if 'tmp' in os.path.split(i)[1]:
                os.remove(i)

    threads = []
    nloops = range(len(seriesPairs))
    delFiles = []
    for i in nloops:
        file = seriesPairs[i][1] + '.mp3'
        if os.path.exists(file):
            delFiles.append(i)

    for i in range(len(delFiles)):
        try:
            seriesPairs[delFiles[i]][1] = seriesPairs[delFiles[i]][1] = None
        except:
            pass
    nloops = range(len(seriesPairs))
    for i in nloops:
        t = threading.Thread(target=MyThread(download, (seriesPairs[i], root), download.__name__))
        threads.append(t)
    for i in nloops:  # start threads 此处并不会执行线程，而是将任务分发到每个线程，同步线程。等同步完成后再开始执行start方法
        threads[i].start()
    for i in nloops:  # jion()方法等待线程完成
        threads[i].join()

    os.chdir('..')
    file = open('PreachesListDone.txt', 'a+', encoding='utf-8')

    # make sure the useless downloading is excluded or process interrupted unexpectedly
    tmp = noFile = ''
    for i in filelist:
        if os.path.isfile(i):
            if 'tmp' in os.path.split(i)[1]:
                tmp = 'exists tmp'

    if len(filelist) == 0:
        noFile = 'no files'
    #comment end

    file.write(root + tmp + noFile + '\n')
    file.close()

def openSeries(urlList):
    file = open('PreachesListDone.txt', 'r', encoding='utf-8')
    content = file.readlines()
    file.close()
    content = ''.join(content).strip('\n')
    print(content)
    for series in urlList:
        title = series[0]
        urlSeries = series[1]
        if content.find(title) != -1:
            pass
        url = 'https://www.fuyin.tv' + urlSeries
        try:
            seriesPairs = openOneSeries(url)
        except:
            file = open('PreachesListDone.txt', 'a+', encoding='utf-8')
            file.write(series[0] + ' failed\n')
            file.write(url + '\n')
            file.close()
            continue
        startSeries(title, seriesPairs)

def openOneSeries(url):
    decoding = 'gbk'
    req = urllib.request.urlopen(url)
    body = req.read().decode(decoding)
    rule = 'data-link=\".*mp3\"'
    rule = re.compile(rule)
    links = rule.findall(body)
    if len(links) == 0:
        return []
    mp3Links = []
    for link in links:
        link = link[link.find('"')+1: -1]
        mp3Links.append(link)

    rule = 'a title=[\"](.*?)[\"]'
    rule = re.compile(rule, re.S)
    titles = rule.findall(body)
    seriesPair = []
    for i in range(len(mp3Links)):
        titles[i] = titles[i].replace('\r','')\
            .replace('?','').replace('？','').replace('\t','')
        try:
            seriesPair.append([mp3Links[i], titles[i]])
        except:
            print(titles)
    return seriesPair

def createDirs(dirList):
    for i in range(len(dirList)):
        dirList[i][0] = dirList[i][0].strip('\t')
        dirList[i][0] = dirList[i][0].replace("?","")
        dirList[i][0] = dirList[i][0].replace("？", "")
        if not os.path.exists(dirList[i][0]):
            try:
                os.mkdir(dirList[i][0])
            except:
                pass


def main():
    # os.chdir('D:\\Preaches')
    # print(os.getcwd())
    urlList = genFileList(decoding = None, gen=False)
    # createDirs(urlList)
    openSeries(
        # [['爱可以再更多一点点', '/content/view/movid/1746/']]
        urlList
    )

main()

