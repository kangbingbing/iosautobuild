#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 使用命令
#./autobuild.py -p youproject.xcodeproj -s schemename
#./autobuild.py -w youproject.xcworkspace -s schemename
# python3 autobuild.py -w ../ios/HJZT.xcworkspace -s HJZT

import argparse
import subprocess
import requests
import os
import smtplib
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import time

#Configuration for iOS build setting
# 测试环境1  生产环境0
TEST = 0
CONFIGURATION = "Release"
EXPORT_OPTIONS_PLIST = "exportOptions.plist"
#会在桌面创建输出ipa文件的目录
EXPORT_MAIN_DIRECTORY = "~/Desktop/"

# configuration for pgyer
DOWNLOAD_BASE_URL = "https://www.xcxwo.com"
USER_KEY = "197fbb5c7db899892a0ea58abcxxxxx"
API_KEY = "f722ad29992f58369d84ed726xxxxx"

#应用安装方式 1：公开安装，2：密码安装，3：邀请安装
PGYER_INSTALLTYPE = "2"
#设置从蒲公英下载应用时的密码
PGYER_PASSWORD = "123"
#设置蒲公英描述信息
PGYER_DESC = ""

mailto_list=['123456@qq.com']
mail_host="smtp.163.com"
sender = "xxxx@163.com"

startTime = time.time()

def send_mail(to_list,sub,content):
    msg = MIMEText(content,'html','utf-8')
    msg['Subject'] = sub
    msg['From'] = formataddr(parseaddr('app名字 iOS<%s>' % sender))
    msg['To'] = ";".join(to_list)
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(sender,"password")
        server.sendmail(sender, to_list, msg.as_string())
        server.close()
        return True
    except Exception as e:
        print (str(e))
        return False

def cleanArchiveFile(archiveFile):
	cleanCmd = "rm -r %s" %(archiveFile)
	process = subprocess.Popen(cleanCmd, shell = True)
	process.wait()
	print ("cleaned archiveFile: %s" %(archiveFile))


def parserUploadResult():
	x = "test" if TEST == 1 else "release"
	downUrl = DOWNLOAD_BASE_URL + "/" + x
	updateTime = (time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(time.time() + 28800)))
	print ("Upload Success")
	print ("DownUrl is:" + downUrl + "\n" + "UpdateTime is:" + updateTime)
	content = ('''
        <!DOCTYPE html>
        <html>
        <head>
        <title>app名字</title>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no minimal-ui">
        </head>
        <body>

        <div style="text-align:center; padding:20px 0px 0px 0px">
                <img src="https://cdn-app-icon.pgyer.com/a/b/1/1/4/ab114f51572c577981795f070a6a568e?x-oss-process=image/resize,m_lfit,h_100,w_100/format,jpg" style="width:60px; height:60px; border-radius:10px;" />
        </div>                    
        <div style="text-align:center;color:#333;font-size:20px;">
            <b>app名字</b>
        </div>
        <div style="text-align:center; padding: 15px 0px">
                <div style="background: #1abc9c!important; padding: 5px 0px 5px 0px; display: inline-block;border-radius:30px; ">
                    <a href="%s" target="_blank" style="font-size: 15px; padding: 3px 30px; color: #fff; text-decoration:none;">点击下载</a>
                </div>

                <div  style="padding: 15px 0px">
                    <a href="%s" target="_blank" style="color: #1abc9c">%s</a>
                    <br />
                    密码: 123
                    <br />
                    <span style="font-size: 14px; color: #999;">%s</span>
                </div>
                <img src="https://www.xcxwo.com/app/qrcode/%s" style="width:100px; height:100px;" />
        </div>
        </body>
        </html>
    ''') % (downUrl, downUrl, downUrl, updateTime, x)
	if send_mail(mailto_list, "xxx iOS在蒲公英上发布完成", content):
		print ("Send Email Success")
	else:
		print ("Upload Fail!")

def checkUploadResult(data):
	print ("Check Upload Result....")
	param = {"_api_key":API_KEY,"buildKey":data["key"]}
	r = requests.get("https://www.xcxwo.com/apiv2/app/buildInfo",params=param)
	if r.status_code == requests.codes.ok:
		result = r.json()
		if result["code"] == 1247:
			print (result["message"])
			time.sleep(5)
			checkUploadResult(data)
		elif result["code"] == 1246:
			print ("App Publish Fail!")
		else:
			parserUploadResult()
			print ("Upload Success")

	else:
		print ('HTTPError,Code:'+r.status_code)

def uploadIpaToPgyer(data,ipaPath):
    ipaPath = os.path.expanduser(ipaPath)
    files = {'file': open(ipaPath, 'rb')}
    headers = {'enctype':'multipart/form-data'}
    payload = {'key':data["key"],'signature':data["params"]["signature"], 'x-cos-security-token':data["params"]["x-cos-security-token"]}
    print ("Uploading....")
    r = requests.post(data["endpoint"], data = payload ,files=files,headers=headers)
    if r.status_code == 204:
        # parserUploadResult()
        checkUploadResult(data)
    else:
        print ('HTTPError,Code:'+ r.reason)
    
	
def getUploadToken(ipaPath):
	endTime = time.time()
	print ("[编译]共使用%d分%d秒" % ((endTime - startTime) / 60, (endTime - startTime) % 60))
	print ("Get Upload Token....")
	param = {"_api_key":API_KEY,"buildType":"ios","buildInstallType":PGYER_INSTALLTYPE,"buildPassword":PGYER_PASSWORD,"buildUpdateDescription":PGYER_DESC}
	r = requests.post("https://www.xcxwo.com/apiv2/app/getCOSToken",params=param)
	if r.status_code == requests.codes.ok:
		result = r.json()
		print ("Get Token Success")
		uploadIpaToPgyer(result["data"],ipaPath)
	else:
		print ('HTTPError,Code:'+r.status_code)
    

#创建输出ipa文件路径: ~/Desktop/{scheme}{2017-1-28_10-08-10}
def buildExportDirectory(scheme):
	dateCmd = 'date "+%Y-%m-%d_%H-%M-%S"'
	process = subprocess.Popen(dateCmd, stdout=subprocess.PIPE, shell=True)
	(stdoutdata, stderrdata) = process.communicate()
	exportDirectory = "%s%s%s" %(EXPORT_MAIN_DIRECTORY, scheme, stdoutdata.strip().decode())
	return exportDirectory

def buildArchivePath(tempName):
	process = subprocess.Popen("pwd", stdout=subprocess.PIPE)
	(stdoutdata, stderrdata) = process.communicate()
	archiveName = "%s.xcarchive" %(tempName)
	archivePath = str(stdoutdata.strip().decode()) + '/' + archiveName
	return archivePath


def getIpaPath(exportPath,scheme):
	cmd = "ls %s" %(exportPath)
	process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
	(stdoutdata, stderrdata) = process.communicate()
	ipaName = stdoutdata.strip()
	ipaPath = exportPath + "/" + scheme + '.ipa'
	print (ipaPath)
	return ipaPath

def exportArchive(scheme, archivePath):
	exportDirectory = buildExportDirectory(scheme)
	if TEST:
		global EXPORT_OPTIONS_PLIST
		EXPORT_OPTIONS_PLIST = "exportOptionsTest.plist"
		print (EXPORT_OPTIONS_PLIST)
	exportCmd = "xcodebuild -exportArchive -archivePath %s -exportPath %s -exportOptionsPlist %s" %(archivePath, exportDirectory, EXPORT_OPTIONS_PLIST)
	process = subprocess.Popen(exportCmd, shell=True)
	(stdoutdata, stderrdata) = process.communicate()

	signReturnCode = process.returncode
	if signReturnCode != 0:
		print ("export %s failed" %(scheme))
		return ""
	else:
		return exportDirectory

def buildProject(project, scheme):
	archivePath = buildArchivePath(scheme)
	print ("archivePath: " + archivePath)
	archiveCmd = 'xcodebuild -project %s -scheme %s -configuration %s archive -archivePath %s -destination generic/platform=iOS' %(project, scheme, CONFIGURATION, archivePath)
	process = subprocess.Popen(archiveCmd, shell=True)
	process.wait()

	archiveReturnCode = process.returncode
	if archiveReturnCode != 0:
		print ("archive workspace failed" )
		cleanArchiveFile(archivePath)
	else:
		exportDirectory = exportArchive(scheme, archivePath)
		cleanArchiveFile(archivePath)
		if exportDirectory != "":		
			ipaPath = getIpaPath(exportDirectory,scheme)
			getUploadToken(ipaPath)

def buildWorkspace(workspace, scheme):
	archivePath = buildArchivePath(scheme)
	print ("archivePath: " + archivePath)
	archiveCmd = 'xcodebuild -workspace %s -scheme %s -configuration %s archive -archivePath %s -destination generic/platform=iOS' %(workspace, scheme, CONFIGURATION, archivePath)
	process = subprocess.Popen(archiveCmd, shell=True)
	process.wait()

	archiveReturnCode = process.returncode
	if archiveReturnCode != 0:
		print ("archive workspace %s failed" %(workspace))
		cleanArchiveFile(archivePath)
	else:
		exportDirectory = exportArchive(scheme, archivePath)
		cleanArchiveFile(archivePath)
		if exportDirectory != "":		
			ipaPath = getIpaPath(exportDirectory,scheme)
			getUploadToken(ipaPath)

def xcbuild(options):
	project = options.project
	workspace = options.workspace
	scheme = options.scheme
	desc = options.desc
	
	if desc is not None:
		global PGYER_DESC
		PGYER_DESC = desc

	if project is None and workspace is None:
		pass
	elif project is not None:
		buildProject(project, scheme)
	elif workspace is not None:
		buildWorkspace(workspace, scheme)

def main():
	
	parser = argparse.ArgumentParser()
	parser.add_argument("-w", "--workspace", help="Build the workspace name.xcworkspace.", metavar="name.xcworkspace")
	parser.add_argument("-p", "--project", help="Build the project name.xcodeproj.", metavar="name.xcodeproj")
	parser.add_argument("-s", "--scheme", help="Build the scheme specified by schemename. Required if building a workspace.", metavar="schemename")
	parser.add_argument("-d", "--desc", help="Build the Desc", metavar="descname")
	options = parser.parse_args()

	print ("options: %s" % (options))

	xcbuild(options)

if __name__ == '__main__':
	main()
	endTime = time.time()
	print ("[打包]共使用%d分%d秒" % ((endTime - startTime) / 60, (endTime - startTime) % 60))