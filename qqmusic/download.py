# -*- coding: utf-8 -*-
# @Author: xzh0723
# @Date:   2019-05-15 09:07:36
# @Last Modified time: 2019-05-25 09:10:22
import requests
from urllib.parse import quote
import json
import os 

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
}

def get_song_list(keyword):
	keyword = quote(keyword)
	url = 'https://c.y.qq.com/soso/fcgi-bin/client_search_cp?ct=24&qqmusic_ver=1298&new_json=1&remoteplace=txt.yqq.song&searchid=56837819165005692&t=0&aggr=1&cr=1&catZhida=1&lossless=0&flag_qc=0&p=1&n=10&w=%s&g_tk=733332777&loginUin=2995438815&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0' % keyword
	response = requests.get(url, headers=HEADERS).text.encode(
	    'gbk', 'ignore').decode('gbk').split('callback')[-1].strip('()')
	result = json.loads(response)
	if result.get('data') and result.get('data').get('song') and result.get('data').get('song').get('list'):
		songs = result.get('data').get('song').get('list')
		return songs
 
def print_info(songs):
	info = {}
	for num, song in enumerate(songs):
		info['number'] = num
		info['songname'] = song.get('name')
		singer_length = len(song.get('singer'))
		singers = []
		for i in range(singer_length):
			singers.append(song.get('singer')[i].get('name'))
		info['singers'] = ('/').join(singers)
		info['album_name'] = song.get('album').get('name')
		time = song.get('interval')
		m, s = divmod(time, 60)
		info['time'] = '%02d:%02d' % (m, s)
		print(info)

def get_mp3(songs, num):
	headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Origin': 'https://y.qq.com',
    'Referer': 'https://y.qq.com/portal/player.html',
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
	}
	base_url = 'https://u.y.qq.com/cgi-bin/musicu.fcg?&data=%s'
	songmid = songs[int(num)].get('mid')
	data = '{' \
		'"req": {' \
			'"module": "CDN.SrfCdnDispatchServer",' \
			'"method":"GetCdnDispatch", ' \
			'"param": {' \
				'"guid": "938739982",' \
				'"calltype": 0,' \
				'"userip":""' \
			'}' \
		'},' \
		'"req_0": {' \
			'"module":"vkey.GetVkeyServer",' \
			'"method": "CgiGetVkey",' \
			'"param": {' \
				'"guid": "938739982",' \
				'"songmid": ["%s"],' \
				'"songtype": [0],' \
				'"uin": "2995438815",' \
				'"loginflag": 1,' \
				'"platform":"20"' \
			'}' \
		'},' \
		'"comm": {' \
			'"uin": 2995438815,' \
			'"format": "json",' \
			'"ct": 24,' \
			'"cv":0' \
		'}' \
	'}' % songmid
	url = base_url % quote(data)
	response = requests.get(url, headers=headers)
	result = json.loads(response.text)
	purl = result.get('req_0').get('data').get('midurlinfo')[0].get('purl')
	url = 'http://dl.stream.qqmusic.qq.com/' + purl
	return url

def download_mp3(url, songname):
	response = requests.get(url, headers=HEADERS)
	print(response)
	path = os.path.abspath('D:\qq音乐下载器\单曲')
	if response.status_code == 200:
		print('正在下载')
		save_music = path + '\\' + songname + '.m4a'
		with open(save_music, 'wb') as f:
			f.write(response.content)
			print('下载成功')
	else:
		print('网络请求错误')
			
def run():
	while True:
		name = input('请输入你要下载的歌曲:')
		songs = get_song_list(name)
		if songs == []:
			print('没有搜索到相关歌曲！')
		else:
			print_info(songs)
			num = input('请输入你要下载的歌曲编号:')
			url = get_mp3(songs, num)
			if url == 'http://dl.stream.qqmusic.qq.com/':
				print('你下载的歌曲不存在,or 请开通VIP下载!')
				answer = input('是否需要继续下载列表中其他版本歌曲？(yes/no)')
				if answer == 'yes':
					num = input('请输入歌曲编号:')
					url = get_mp3(songs, num)
					songname = songs[int(num)].get('name')
					download_mp3(url, songname)
			else:
				songname = songs[int(num)].get('name')
				download_mp3(url, songname)
				
			flag = input('如需继续下载请按Enter继续，否则按0结束程序')
			if flag == '0':
				break
				
if __name__ == '__main__':
	run()
