import re
import os
import json
import requests
from urllib.parse import quote

base_url = 'http://m.music.migu.cn/migu/remoting/scr_search_tag?rows=20&type=2&keyword={}&pgc=1'
headers = {
    'Accept': 'application/json, text/js, */*; q=0.01',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Referer': 'http://m.music.migu.cn/v3/search?keyword=%E7%BB%BF%E8%89%B2',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Mobile Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}


def download(url):
    try:
        response = requests.get(url, headers=headers)
        result = json.loads(response.text)
        if result.get('musics'):
            songs = result.get('musics')
            for song in songs:
                singer = song.get('singerName')
                songname = song.get('songName')
                lyric = song.get('lyrics')
                src = song.get('mp3')
                print(singer, songname)
                print('是否下载该歌曲？(yes/其他任意键结束)')
                answer = input()
                if answer == 'yes':
                    path = os.path.abspath('D:\咪咕下载器\纠结伦')
                    key = songname
                    value = src
                    song = {key: value}
                    response = requests.get(value, headers=headers)
                    for key, value in song.items():
                        print('正在下载{}'.format(key))
                        save_mp3 = path + '\\' + key + '.mp3'
                        with open(save_mp3, 'wb') as f:
                            f.write(response.content)
                            print('下载成功')
                        print(lyric)
                        print('是否需要显示歌词：(yes/no)')
                        anwser = input()
                        if anwser == 'yes':
                            response = requests.get(lyric)
                            lrc = response.text
                            lyric = re.sub('\[.*\]', '', lrc)
                            print(lyric)
                #else:
                #    break
    except:
        print('请检查该歌曲是否存在')
        download(url)

if __name__ =='__main__':
    print('请输入歌曲名称：')
    text = input()
    url = base_url.format(quote(text))
    download(url)
