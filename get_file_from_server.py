import urllib, urllib2, cookielib, re, time
import json
import time

server_url = "http://nat-traversal.tplinkcloud.com:5000/download/"
server_login = "http://nat-traversal.tplinkcloud.com:5000/login"

email_list = []
result_list = []

buf = "%0.0f" % time.time()
save_file = buf + "_data.csv"
def get_full_server_url():
	return server_url

def post(url, data):
	req = urllib2.Request(url)
	data = urllib.urlencode(data)
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
	try:
		response = opener.open(req, data)
	except:
		print "post open URL Error " + url
		return None
	return response.headers['Set-Cookie']

def login_server(url, user_name, password, count):
	data = {
		'username' : user_name,
		'password' : password,
	}
	for i in range(count):
		ret = post(url, data)
		if None == ret:
			continue
		else:
			return ret

def get_year_month_info(buf):
	"""<a href="..">..</a><br><a href="/download/201511/">201511/</a>"""
	tmp = re.findall(buf, '/.*/')
	if tmp is not None:
		print(tmp.__dict__)

def get_html(url, cookie, count):
	g = urllib2.Request(url)
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
	g.add_header('Cookie', cookie)
	g.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 5.1; rv:12.0) Gecko/20100101 Firefox/12.0')
	g.add_header('Connection', 'keep-alive')
	g.add_header('Referer', server_url + "201511")
	g.add_header('Content-Type', 'application/x-www-form-urlencoded')
	for i in range(count):
		try:
			resp = opener.open(g)
		except:
			print "open url error " + url
			resp = None
		if resp == None:
		 	continue
		else:
		 	break
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

def add_result(p2p_data):
	for item in result_list:
		if item.same_item(p2p_data):
			item.count = item.count + 1
			return
	result_list.append(p2p_data)
	return

def output_all(p2p_data_list, save_file):
	for item in p2p_data_list:
		if item.printable == True:
			item.output(save_file)

def get_single_day_files(single_day, cookie, count):
	files_dir_buf = get_html(server_url + "201511/" + single_day + '/', cookie, count)
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
			buf = get_html(full_name, cookie, count)
			if buf is None:
				continue

			a = p2p_data()
			a.file_name = tmp_name[0]
			for line in buf.split("\n"):
			 	a.get_user_info(line)
			add_result(a)

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
	printable = False
	count = 0

	def output(self, file_name):
		out_buf = self.result + "," + self.predict_result + "," + self.nat_type + "," +\
			self.description + "," + self.isp + "," + self.country + "," + self.city + "," +\
			self.network + "," + self.vendor + "," +\
			self.model + "," + self.wan_ip + "," + self.email + "," + self.file_name + "," +\
			str(self.count) + "\n"
		fd = open(file_name, "a+")
		fd.write(out_buf)
		fd.close

	def same_item(self, p2p_data):
		if p2p_data.email == self.email and \
			p2p_data.isp == self.isp and \
			p2p_data.model == self.model and \
			p2p_data.network == self.network:
			print "The same item" + self.email + self.file_name
			return True
		return False

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
			if json_dict['Vendor'] != "":
				self.vendor = json_dict['Vendor']
			if json_dict['Model'] != "":
				self.model = json_dict['Model']
			if json_dict['WAN'] != "":
				self.wan_ip = json_dict['WAN']
			self.printable = True
			self.count = 1
			if self.email not in email_list:
				email_list.append(self.email)
		if 'NAT Type' in json_dict:
			self.nat_type = json_dict['NAT Type']
			self.nat_type = self.nat_type.replace(", ", "_")
			if self.nat_type.find("Independent") == 0:
				self.predict = "Success"
		if 'Predict Result' in json_dict:
			self.result = json_dict['Predict Result']

if __name__ == '__main__':
	print "hello world"
	import sys
	user_name = sys.argv[1]
	password = sys.argv[2]

	# set socket timeout 5s
	urllib2.socket.setdefaulttimeout(5)
	# set retry count == 3
	cookie = login_server(server_login, user_name, password, 3)
	for i in range(12, 24):
		print str(i)
		get_single_day_files(str(i), cookie, 3)
	output_all(result_list, save_file)

	for email in email_list:
		print email

