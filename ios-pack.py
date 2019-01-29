# coding:utf-8

import subprocess
import time
import os
import smtplib
from email.mime.text import MIMEText
from email import encoders
from email.header import Header
from email.utils import parseaddr, formataddr

product_path = "" #项目路径 *
product_name = "" #项目名称 *
scheme_name = "" #scheme名称，一般和项目名称相同 *
build_type = "Release" # Debug，Release *

bit_code = "true" # 项目中是否打开bitcode，与项目中保持一致 *
build_type = "" # development app-store enterprise *
bundle_identifier = "" # *
profile_type = "PL_adHoc" #配置文件名称 *
sign_cer = "iPhone Distribution" #  *
team_id = "" #团队id，在开发账号中找到 *

# fir相关信息
fir_token = "" #用于登录fi的用户的token *

# 邮件相关信息
from_address = "" #发送人邮件地址 *
to_address = "" #接收人邮件地址，最好是163邮箱 *
passowrd = "" # 接收人邮箱的授权码，非密码 *
smtp_server = "smtp.163.com"



class AutoArchive(object):

	def __init__(self):
		pass

	def homePath(self):
		home_path = "/%s%s" % (os.getcwd(),product_name,time.strftime('%Y-%m-%d',time.localtime(time.time())))
		if os.path.exists(home_path) == False:
			mkdir_command = "mkdir %s" % home_path
			subprocess.call(mkdir_command,shell=True)
		return home_path

# /.xcarchive是个文件夹，archive的文件都在这个文件夹下
	def archivePath(self):
		archive_path = "%s/%s.xcarchive" % (self.homePath(),product_name)
		if os.path.exists(archive_path) == False:
			mkdir_command = "mkdir %s" % archive_path
			subprocess.call(mkdir_command,shell=True)
		return archive_path

# 导出ipa包所需要的plist配置文件
	def exportOptionsPlist(self):
		homePath = self.homePath()
		exportOptionsPlistPath = '%s/exportcg.plist' % homePath
		if os.path.exists(exportOptionsPlistPath) == True:
			print ('文件已存在')
		else:
			fp = open(exportOptionsPlistPath,'w')
			fp.write('<?xml version="1.0" encoding="UTF-8"?>')
			fp.write('<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">')
			fp.write('<plist version="1.0">')
			fp.write('<dict>')
			fp.write('<key>compileBitcode</key>')
			fp.write('<%s/>' % bit_code)
			fp.write('<key>method</key>')
			fp.write('<string>%s</string>' % build_type)
			fp.write('<key>provisioningProfiles</key>')
			fp.write('<dict>')
			fp.write('<key>%s</key>' % bundle_identifier)
			fp.write('<string>%s</string>' % profile_type)
			fp.write('</dict>')
			fp.write('<key>signingCertificate</key>')
			fp.write('<string>%s</string>' % sign_cer)
			fp.write('<key>signingStyle</key>')
			fp.write('<string>manual</string>')
			fp.write('<key>stripSwiftSymbols</key>')
			fp.write('<true/>')
			fp.write('<key>teamID</key>')
			fp.write('<string>%s</string>' % team_id)
			fp.write('<key>thinning</key>')
			fp.write('<string>&lt;none&gt;</string>')
			fp.write('</dict>')
			fp.write('</plist>')
			fp.close()
		return exportOptionsPlistPath


# 归档之前先clean一下工程，防止一些莫名其妙的错误
	def clean(self):
		print("\n\n====================开始clean操作==========================")
		homePath = self.homePath()
		# 清空文件夹
		clear_commend = "rm -rf %s" % homePath
		subprocess.call(clear_commend,shell=True)

		start = time.time()
		budid_commend = 'xcodebuild clean -workspace %s/%s.xcworkspace -scheme %s -configuration %s' % (product_path,product_name,product_name,build_type)
		budid_commend_run = subprocess.Popen(budid_commend,shell=True)
		budid_commend_run.wait()
		end = time.time()

		result_code = budid_commend_run.returncode
		if result_code != 0:
			print("======================clean失败,用时:%.2f秒======================" % (end - start))
		else:
			print("======================clean成功,用时:%.2f秒======================" % (end - start))

	def archive(self):
		print("\n\n=================开始archive操作====================")

		#创建archive的路径
		archive_path = self.archivePath()

		#开始打包
		start = time.time()
		archive_command = 'xcodebuild archive -workspace %s/%s.xcworkspace -scheme %s -configuration %s -archivePath %s' % (product_path,product_name,product_name,build_type,archive_path)
		archive_command_run = subprocess.Popen(archive_command,shell=True)
		archive_command_run.wait()
		end = time.time()

		result_code = archive_command_run.returncode
		if result_code != 0:
			print("==================archive失败,用时:%.2f秒====================" % (end - start))
		else:
			print("==================archive成功,用时:%.2f秒====================" % (end - start))

	def export(self):
		print("\n\n==================开始export操作====================")

		export_path = self.homePath()
		archive_path = self.archivePath()
		exportOptionsPlist_path = self.exportOptionsPlist()

		#开始导出
		start = time.time()
		export_command = 'xcodebuild -exportArchive -archivePath %s -exportPath %s -exportOptionsPlist %s' % (archive_path,export_path,exportOptionsPlist_path)
		export_command_run = subprocess.Popen(export_command,shell=True)
		export_command_run.wait()
		end = time.time()

		result_code = export_command_run.returncode
		if result_code != 0:
			print("==================export失败,用时:%.2f秒====================" % (end - start))
		else:
			print("==================export成功,用时:%.2f秒====================" % (end - start))
		os.remove(exportOptionsPlist_path)

	def upload(self):
		print("\n\n====================开始upload操作==========================")
		ipa_path = '%s/%s.ipa' % (self.homePath(),product_name)

		start = time.time()
		fir_login_str = 'fir login %s' % fir_token
		subprocess.call(fir_login_str,shell=True)

		fir_upload_str = 'fir publish %s -Q' % ipa_path
		fir_upload_command = subprocess.Popen(fir_upload_str,shell=True)
		fir_upload_command.wait()
		end = time.time()

		result_code = fir_upload_command.returncode
		if result_code != 0:
			print("==================upload失败,用时:%.2f秒====================" % (end - start))
		else:
			print("==================upload成功,用时:%.2f秒====================" % (end - start))
		return result_code

	def _format_addr(self,s):
		name, addr = parseaddr(s)
		return formataddr(( \
        Header(name, 'utf-8').encode(), \
        addr.encode('utf-8') if isinstance(addr, unicode) else addr))

	def sendEmail(self,content):
		print("\n====================开始sendemail操作==========================")
		start = time.time()
		message = MIMEText(content,'plain','utf-8')
		message['From'] = self._format_addr(u'那个谁谁谁 <%s>' % from_address)
		message['To'] = self._format_addr(u'测试 <%s>' % to_address)
		message['Subject'] = Header(content,'utf-8').encode()

		server = smtplib.SMTP(smtp_server,25)
		server.set_debuglevel(1)
		server.login(from_address,passowrd)
		server.sendmail(from_address,[to_address],message.as_string())
		server.quit()
		end = time.time()
		print("==================send完成,用时:%.2f秒====================" % (end - start))

	def start(self):
		start = time.time()
		self.clean()
		self.archive()
		self.export()
		result_code = self.upload()
		content = ''
		if result_code != 0:
			content = '打包未成功，请查看原因'
		else:
			content = '%s应用已上传至fir.im，请下载测试' % product_name
		self.sendEmail(content)
		end = time.time()
		print("\n====================操作完成，总用时:%.2f秒=========================" % (end - start))




if __name__ == '__main__':
	archive = AutoArchive()
	archive.start()
