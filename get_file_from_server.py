import urllib, urllib2, cookielib, re, time
import json

server_url = "http://nat-traversal.tplinkcloud.com:5000/download/"
server_login = "http://nat-traversal.tplinkcloud.com:5000/login"
save_file = "data.csv"

def get_full_server_url():
	return server_url

def post(url, data):
	req = urllib2.Request(url)
	data = urllib.urlencode(data)
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
	response = opener.open(req, data)
	return response.headers['Set-Cookie']

def login_server(url, user_name, password):
	data = {
		'username' : user_name,
		'password' : password,
	}
	return post(url, data)

def get_year_month_info(buf):
	"""<a href="..">..</a><br><a href="/download/201511/">201511/</a>"""
	tmp = re.findall(buf, '/.*/')
	if tmp is not None:
		print(tmp.__dict__)
def get_url(url, cookie):
	g = urllib2.Request(url)
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
	g.add_header('Cookie', cookie)
	g.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 5.1; rv:12.0) Gecko/20100101 Firefox/12.0')
	g.add_header('Connection', 'keep-alive')
	g.add_header('Referer', server_url + "201511")
	g.add_header('Content-Type', 'application/x-www-form-urlencoded')
	try:
		resp = opener.open(g)
	except:
		print "open url error"
		return None
	return resp.read()

""" return list of files name """
def parse_files_dir(buf):
	"""href="/download/201511/23/022516-26007189-IP"""
	try:
		tmp_re = re.findall("href=\"(.+?)\"", buf)
	except TypeError:
		print "parse files dir error " + buf
		return None
	return tmp_re

def get_single_day_files(single_day, cookie):
	files_dir_buf = get_url(server_url + "201511/" + single_day + '/', cookie)
	if files_dir_buf is None:
		print "Could not get files directory"
		return None
	files_name_list = parse_files_dir(files_dir_buf)
	if files_name_list is None:
		return None
	for name in files_name_list:
		if name == "..":
			continue
		tmp_name = re.findall("/.+/(.+?)$", name)
		if tmp_name is not None:
			print "File Name\t" + tmp_name[0]
			full_name = server_url + "201511/" + single_day + '/' + tmp_name[0]
			buf = get_url(full_name, cookie)
			if buf is None:
				break

			a = p2p_data()
			a.name = file_name = tmp_name[0]
			for line in buf.split("\n"):
			 	a.get_user_info(line)
			a.output(save_file)

			"""
			if need to write to the file, use the codes.
			if buf is not None:
				fd = open( save_dir + tmp_name[0], "a+")
				fd.write(buf)
				fd.close()
			"""

class p2p_data:
	result = ""
	predict_result = "Unknow" 
	email = "" 
	country = "" 
	city = ""
	isp = "" 
	network = "Unknow"
	vendor = "Unknow" 
	model = "Unknow"
	wan_ip = "Unknow" 
	file_name = ""
	nat_type = "" 
	description = "Unknow"
	def __init__(self):
		print "123"

	def output(self, file_name):
		out_buf = self.result + "," + self.predict_result + "," + self.nat_type + "," +\
			self.description + "," + self.isp + "," + self.country + "," + self.city + "," +\
			self.network + "," + self.vendor + "," +\
			self.model + "," + self.wan_ip + "," + self.file_name + "\n"
		fd = open(file_name, "a+")
		fd.write(out_buf)
		fd.close

	def get_user_info(self, buf_line):
		"""{"Email":"tim.xiang@tp-link.com",
			"Country":"Singapore",
			"City":"Adjuneid",
			"ISP":"Starhub",
			"Network":"Office Network",
			"Vendor": "",
			"Model":"DIR-868L",
			"WAN":"27.54.61.88"}"""
		try:
			json_dict = json.loads(buf_line)
		except TypeError:
			print "does not json type"
			return None
		except ValueError:
			print "No JSON object could be decoded"
			return None
		if 'Vendor' in json_dict:
			self.email = json_dict['Email']
			self.country = json_dict['Country']
			self.city = json_dict['City']
			self.isp = json_dict['ISP']
			self.network = json_dict['Network']
			self.vendor = json_dict['Vendor']
			self.model = json_dict['Vendor']
			self.wan_ip = json_dict['WAN']
		if 'NAT Type' in json_dict:
			self.nat_type = json_dict['NAT Type']
		if 'Predict Result' in json_dict:
			self.result = json_dict['Predict Result']

if __name__ == '__main__':
	print "hello world"
	import sys
	user_name = sys.argv[1]
	password = sys.argv[2]

	cookie = login_server(server_login, user_name, password)
	get_single_day_files("23", cookie)
	get_single_day_files("24", cookie)
#	buf = """{"Email":"tim.xiang@tp-link.com", "Country":"Singapore", "City":"Adjuneid", "ISP":"Starhub",\
#	       "Network":"Office Network","Vendor": "D-LINK","Model":"DIR-868L","WAN":"27.54.61.88"}"""
#	buf_test = """{"NAT Type":6 ,"NAT Type":"Independent Mapping, Port Dependent Filter"}"""
#	a = p2p_data()
#	a.get_user_info(buf)
#	a.output("hello")

