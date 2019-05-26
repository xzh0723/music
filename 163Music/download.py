# -*- coding: utf-8 -*-

import requests
import math,random
from Crypto.Cipher import AES
from urllib.request import urlretrieve
from jindutiao import TqdmUpTo
import base64
import codecs
import os
import time
import json
import re
import pymongo

class decrypt_music(object):
    def __init__(self, d):
        self.d = d
        self.e = '010001'
        self.f = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5a" \
                 "a76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46be" \
                 "e255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
        self.g = '0CoJUm6Qyw8W8jud'
        self.random_text = self.get_random_str()

    def get_random_str(self):
        """
        获取一个随机16位字符串
        :return: 随机16位字符串
        """
        str = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        res = ''
        for x  in range(16):
            index = math.floor(random.random() * len(str))
            res += str[index]
        return res

    def aes_encrypt(self, text, key):
        """
        AES加密
        :param text: 待加密密文
        :param key: 密钥
        :return:
        """
        # iv: 偏移量
        iv = '0102030405060708'
        # 注：AES只能加密数字和字母，无法加密中文。
        # 解决方法：在CBC加密模式下，字符串必须补齐长度为16的倍数，且长度指标不能为中文，需转化为unicode编码长度
        pad = 16 - len(text.encode()) % 16
        text = text + pad * chr(pad)
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        # 最后还需要进行base64加密
        msg = base64.b64encode(encryptor.encrypt(text))
        return msg

    def rsa_encrypt(self, value, text, modulus):
        """
        RSA加密
        :param value: 加密指数
        :param text: 待加密密文
        :param modulus: 加密系数
        :return:
        """
        text = text[::-1]
        rs = int(codecs.encode(text.encode('utf-8'), 'hex_codec'), 16) ** int(value, 16) % int(modulus, 16)
        return format(rs, 'x').zfill(256)


    def get_data(self):
        """
        params：进行了两次AES加密
        encSecKey：进行了一次RSA加密
        :return:
        """
        params = self.aes_encrypt(self.d, self.g)
        params = self.aes_encrypt(params.decode('utf-8'), self.random_text)
        encSecKey = self.rsa_encrypt(self.e, self.random_text, self.f)
        return {
            'params': params,
            'encSecKey': encSecKey
        }

class SongDownloader(object):
    def __init__(self):
        self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
                'Cookie':'_iuqxldmzr_=32; _ntes_nnid=8d4ef0883a3bcc9d3a2889b0bf36766a,1533782432391; _ntes_nuid=8d4ef0883a3bcc9d3a2889b0bf36766a; __utmc=94650624; WM_TID=GzmBlbRkRGQXeQiYuDVCfoEatU6VSsKC; playerid=19729878; __utma=94650624.1180067615.1533782433.1533816989.1533822858.9; __utmz=94650624.1533822858.9.7.utmcsr=cn.bing.com|utmccn=(referral)|utmcmd=referral|utmcct=/; WM_NI=S5gViyNVs14K%2BZoVerGK69gLlmtnH5NqzyHcCUY%2BiWm2ZaHATeI1gfsEnK%2BQ1jyP%2FROzbzDV0AyJHR4YQfBetXSRipyrYCFn%2BNdA%2FA8Mv80riS3cuMVJi%2BAFgCpXTiHBNHE%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee84b674afedfbd3cd7d98b8e1d0f554f888a4abc76990b184badc4f89e7af8ece2af0fea7c3b92a91eba9b7ec738e8abdd2b741e986a1b7e87a8595fadae648b0b3bc8fcb3f8eafb69acb69818b97ccec5dafee9682cb4b98bb87d2e66eb19ba2acaa5bf3b6b7b1ae5a8da6ae9bc75ef49fb7abcb5af8879f87c16fb8889db3ec7cbbae97a4c566e992aca2ae4bfc93bad9b37aab8dfd84f8479696a7ccc44ea59dc0b9d7638c9e82a9c837e2a3; JSESSIONID-WYYY=sHwCKYJYxz6ODfURChA471BMF%5CSVf3%5CTc8Qcy9h9Whj6CfMxw4YWTMV7CIx5g6rqW8OBv04YGHwwq%2B%5CD1N61qknTP%2Fym%2BHJZ1ylSH1EabbQASc9ywIT8YvOr%2FpMgvmm1cbr2%2Bd6ssMYXuTlpOIrKqp%5C%2FM611EhmfAfU47%5CSQWAs%2BYzgY%3A1533828139236'
        }
        self.client = pymongo.MongoClient(host='localhost', port=27017)
        self.db = self.client.wangyiyun
        self.proxy_url = 'http://api.http.niumoyun.com/v1/http/ip/get?p_id=228&s_id=2&u=AmFVNwE5B2FSYwAuB0kHOA8gVWldZQsaBVJUUFNV&number=1&port=1&type=1&map=1&pro=0&city=0&pb=1&mr=2&cs=1'

    def get_songs(self, name):
        """
        获取歌曲搜索结果
        :param name: 歌曲名称
        :return: 搜索结果
        """
        d = '{"hlpretag":"<span class=\\"s-fc7\\">","hlposttag":"</span>","s":"%s","type":"1","offset":"0","total":"true","limit":"30","csrf_token":""}' % name
        wyy = decrypt_music(d)
        data = wyy.get_data()
        url = 'https://music.163.com/weapi/cloudsearch/get/web?csrf_token='
        response = requests.post(url,data= data,headers =self.headers).json()
        return response['result']

    def print_info(self, songs):
        """
        获取歌曲列表
        :param songs: 搜索结果
        :return: 歌曲列表
        """
        songs_list = []
        for num, song in enumerate(songs):
            print(num, '歌曲名字：', song['name'], '作者：', song['ar'][0]['name'])
            songs_list.append((song['name'], song['id']))
        return songs_list

    def get_mp3(self, id):
        """
        获取歌曲下载地址
        :param id: 歌曲ID
        :return: mp3地址
        """
        d = '{"ids":"[%s]","br":320000,"csrf_token":""}' % id
        wyy = decrypt_music(d)
        data = wyy.get_data()
        url = 'https://music.163.com/weapi/song/enhance/player/url?csrf_token='
        response = requests.post(url, data=data, headers=self.headers).json()
        # print(response)
        return response['data'][0]['url']

    def download_mp3(self, url, filename):
        """
        下载歌曲
        :param url: mp3地址
        :param filename: 下载文件名称
        :return:
        """
        # 获取绝对路径
        abspath = os.path.abspath('.')
        os.chdir(abspath)
        response = requests.get(url, headers=self.headers).content
        path = os.path.join(abspath, filename)
        # 继承至tqdm父类的初始化参数
        with TqdmUpTo(unit='B', unit_scale=True, unit_divisor=1024, miniters=1, desc=f'{filename}.mp4') as t:
            urlretrieve(url, filename=f'{filename}.mp3', reporthook=t.update_to, data=None)
        print('下载完毕,可以在%s   路径下查看' % path + '.mp3')

    def get_lyric(self, songname, id):
        """
        下载歌词
        :param songname: 歌曲名称（用作插入mongodb集合名称）
        :param id: 歌曲ID
        :return:
        """
        url = f'http://music.163.com/api/song/lyric?id={id}&lv=1&kv=1&tv=-1'
        response = requests.post(url, headers=self.headers)
        print(response)
        result = json.loads(response.text)
        lrc = result.get('lrc')
        lyric = {}
        if lrc:
            content = lrc.get('lyric')
            pattern = re.compile(r'\[.*\]')
            content = re.sub(pattern, '', content)
            lyric['lyric'] = content
            print('正在下载歌词')
            self.save_to_mongodb(songname, lyric)

    def get_comment(self, songname, id):
        """
        下载歌曲评论
        :param songname: 歌曲名称（用作插入mongodb集合名称）
        :param id: 歌曲ID
        :return:
        """
        d = '{}'
        #d = '{rid:"", offset:"0", total:"true", limit:"20", csrf_token:""}'
        wyy = decrypt_music(d)
        data = wyy.get_data()
        url = f'https://music.163.com/weapi/v1/resource/comments/R_SO_4_{id}?csrf_token='
        response = requests.post(url, data=data, headers=self.headers).json()
        # print(response)
        totalCount = response['total']
        max_page = int(int(totalCount) / 20) + 1
        print(f'共有{max_page}页评论')
        # 热门评论
        comments = response['hotComments']
        for comment in comments:
            comment_info = {
                'user': {
                    'nickname': comment['user']['nickname'],
                    'avatarUrl': comment['user']['avatarUrl'],
                    'userId': comment['user']['userId']
                },
                'content': comment['content'],
                'commentId': comment['commentId'],
                'releaseTime': time.strftime("%Y-%m-%d %H:%M:%S",
                                             time.localtime(float(int(comment['time']) / 1000))),
                'likedCount': comment['likedCount'],
            }
            # print(comment_info)
            self.save_to_mongodb(songname, comment_info)
        print('热门评论下载成功')
        page = 0
        proxy = self.get_random_proxy()
        while True:
            proxies = {
                'http': f'http//{proxy}',
                'https': f'https://{proxy}'
            }
            if page > int(max_page):
                break
            else:
                d = '{offset:"%s"}' % (page * 20)
                # d = '{rid:"", offset:"0", total:"true", limit:"20", csrf_token:""}'
                wyy = decrypt_music(d)
                data = wyy.get_data()
                response = requests.post(url, data=data, headers=self.headers, proxies=proxies)
                try:
                    comments = response.json()['comments']
                    for comment in comments:
                        comment_info = {
                            'user': {
                                'nickname': comment['user']['nickname'],
                                'avatarUrl': comment['user']['avatarUrl'],
                                'userId': comment['user']['userId']
                            },
                            'content': comment['content'],
                            'commentId': comment['commentId'],
                            'releaseTime': time.strftime("%Y-%m-%d %H:%M:%S",
                                                         time.localtime(float(int(comment['time']) / 1000))),
                            'likedCount': comment['likedCount'],
                        }
                        # print(comment_info)
                        self.save_to_mongodb(songname, comment_info)
                    print(f'第{str(int(page)+1)}页下载完成')
                except:
                    print('更换代理')
                    proxy = self.get_random_proxy()
                    continue
                # 设置下载延迟，防止爬取过快被ban
                time.sleep(random.random() * 10)
            page += 1

    def save_to_mongodb(self, collection, item):
        """
        数据库存储
        :param collection: 集合名称
        :param item: 待插入数据
        :return:
        """
        try:
            self.db[collection].insert(dict(item))
            print('插入成功')
        except Exception as e:
            print('插入失败: ', e.args)

    def get_random_proxy(self):
        """
        使用随机代理下载评论
        :return: 代理IP
        """
        try:
            res = requests.get(self.proxy_url)
            result = res.json()
            ip = result['data'][0]['ip']
            port = result['data'][0]['port']
            proxy = f'{ip}:{port}'
            print(f'成功获取代理{proxy}')
            return proxy
        except Exception as e:
            print('重试')
            self.get_random_proxy()

    def run(self):
        """
        主函数运行
        :return:
        """
        while True:
            name = input('请输入你需要下载的歌曲：')
            songs = self.get_songs(name)
            print(songs)
            if songs['songCount'] == 0:
                print('没有搜到此歌曲，请换个关键字')
            else:
                songs = self.print_info(songs['songs'])
                num = input('请输入需要下载的歌曲，输入左边对应数字即可')
                self.get_lyric(songs[int(num)][0], songs[int(num)][1])
                self.get_comment(songs[int(num)][0], songs[int(num)][1])
                url = self.get_mp3(songs[int(num)][1])
                if not url:
                    print('歌曲需要收费，下载失败')
                else:
                    filename = songs[int(num)][0]
                    self.download_mp3(url, filename)
                flag = input('如需继续可以按任意键进行搜歌，否则按0结束程序')
                if flag == '0':
                    break
        print('程序结束！')

if __name__ == '__main__':
    downloader = SongDownloader()
    downloader.run()
