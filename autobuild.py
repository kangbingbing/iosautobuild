#!/usr/bin/env python
# -*- coding:utf-8 -*-

#./autobuild.py -p youproject.xcodeproj -s schemename
#./autobuild.py -w youproject.xcworkspace -s schemename
#python autobuild.py -w ../HZZG.xcworkspace -s HZZG

import argparse
import subprocess
import requests
import os
import smtplib
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from email.mime.text import MIMEText

#configuration for iOS build setting
CONFIGURATION = "Release"
EXPORT_OPTIONS_PLIST = "exportOptions.plist"
#会在桌面创建输出ipa文件的目录
EXPORT_MAIN_DIRECTORY = "~/Desktop/"

# configuration for pgyer
PGYER_UPLOAD_URL = "http://www.pgyer.com/apiv1/app/upload"
DOWNLOAD_BASE_URL = "http://www.pgyer.com"
USER_KEY = "30a09578ef6545182e25a31589xxxxx"
API_KEY = "d4283457ab19a76eb73e1b9b0e7xxxxx"

#设置从蒲公英下载应用时的密码
PGYER_PASSWORD = ""
#设置描述信息
PGYER_DESC = ""


# 收件人列表
mailto_list=['xxx@qq.com','xxx@163.com']
# 发信服务器
mail_host="smtp.mxhichina.com"
# 用户名
mail_user="kangbing"
# 邮箱提供商
mail_postfix="xxx.com"

def send_mail(to_list,sub,content):
    me="iOS测试包"+"<"+mail_user+"@"+mail_postfix+">"
    msg = MIMEText(content,'plain', 'utf-8')
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)                            #连接服务器
        server.login("kangbing@xxx.com","Kb123")
        server.sendmail(me, to_list, msg.as_string())
        server.close()
        return True
    except Exception, e:
        print str(e)
        return False


def cleanArchiveFile(archiveFile):
	cleanCmd = "rm -r %s" %(archiveFile)
	process = subprocess.Popen(cleanCmd, shell = True)
	process.wait()
	print "cleaned archiveFile: %s" %(archiveFile)


def parserUploadResult(jsonResult):
	resultCode = jsonResult['code']
	if resultCode == 0:
		downUrl = DOWNLOAD_BASE_URL +"/"+jsonResult['data']['appShortcutUrl']
		updateTime = jsonResult['data']['appUpdated']
        print "Upload Success"
        print "DownUrl is:" + downUrl + "\n" + "UpdateTime is:" + updateTime
        # 配置好邮箱信息, 及收件人列表, 把注释打开, 即可进行邮件发送
        # if send_mail(mailto_list,"黄金掌柜iOS在蒲公英上发布完成","   各位同事: \n黄金掌柜项目iOS端蒲公英下载地址: " + downUrl + '\n更新时间:' + updateTime):
        #     print "Send Email Success"
	else:
		print "Upload Fail!"
		print "Reason:"+jsonResult['message']

def uploadIpaToPgyer(ipaPath):
    print "ipaPath:"+ipaPath
    ipaPath = os.path.expanduser(ipaPath)
    ipaPath = unicode(ipaPath, "utf-8")
    files = {'file': open(ipaPath, 'rb')}
    headers = {'enctype':'multipart/form-data'}
    payload = {'uKey':USER_KEY,'_api_key':API_KEY,'publishRange':'2','isPublishToPublic':'2', 'password':PGYER_PASSWORD,'updateDescription':PGYER_DESC}
    print "uploading...."
    r = requests.post(PGYER_UPLOAD_URL, data = payload ,files=files,headers=headers)
    if r.status_code == requests.codes.ok:
         result = r.json()
         parserUploadResult(result)
    else:
        print 'HTTPError,Code:'+r.status_code

#创建输出ipa文件路径: ~/Desktop/{scheme}{2016-12-28_08-08-10}
def buildExportDirectory(scheme):
	dateCmd = 'date "+%Y-%m-%d_%H-%M-%S"'
	process = subprocess.Popen(dateCmd, stdout=subprocess.PIPE, shell=True)
	(stdoutdata, stderrdata) = process.communicate()
	exportDirectory = "%s%s%s" %(EXPORT_MAIN_DIRECTORY, scheme, stdoutdata.strip())
	return exportDirectory

def buildArchivePath(tempName):
	process = subprocess.Popen("pwd", stdout=subprocess.PIPE)
	(stdoutdata, stderrdata) = process.communicate()
	archiveName = "%s.xcarchive" %(tempName)
	archivePath = stdoutdata.strip() + '/' + archiveName
	return archivePath


def getIpaPath(exportPath,scheme):
	cmd = "ls %s" %(exportPath)
	process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
	(stdoutdata, stderrdata) = process.communicate()
	ipaName = stdoutdata.strip()
	ipaPath = exportPath + "/" + scheme + '.ipa'
	print ipaPath
	return ipaPath

def exportArchive(scheme, archivePath):
	exportDirectory = buildExportDirectory(scheme)
	exportCmd = "xcodebuild -exportArchive -archivePath %s -exportPath %s -exportOptionsPlist %s" %(archivePath, exportDirectory, EXPORT_OPTIONS_PLIST)
	process = subprocess.Popen(exportCmd, shell=True)
	(stdoutdata, stderrdata) = process.communicate()

	signReturnCode = process.returncode
	if signReturnCode != 0:
		print "export %s failed" %(scheme)
		return ""
	else:
		return exportDirectory

def buildProject(project, scheme):
	archivePath = buildArchivePath(scheme)
	print "archivePath: " + archivePath
	archiveCmd = 'xcodebuild -project %s -scheme %s -configuration %s archive -archivePath %s -destination generic/platform=iOS' %(project, scheme, CONFIGURATION, archivePath)
	process = subprocess.Popen(archiveCmd, shell=True)
	process.wait()

	archiveReturnCode = process.returncode
	if archiveReturnCode != 0:
		print "archive workspace %s failed" %(workspace)
		cleanArchiveFile(archivePath)
	else:
		exportDirectory = exportArchive(scheme, archivePath)
		cleanArchiveFile(archivePath)
		if exportDirectory != "":		
			ipaPath = getIpaPath(exportDirectory,scheme)
			uploadIpaToPgyer(ipaPath)

def buildWorkspace(workspace, scheme):
	archivePath = buildArchivePath(scheme)
	print "archivePath: " + archivePath
	archiveCmd = 'xcodebuild -workspace %s -scheme %s -configuration %s archive -archivePath %s -destination generic/platform=iOS' %(workspace, scheme, CONFIGURATION, archivePath)
	process = subprocess.Popen(archiveCmd, shell=True)
	process.wait()

	archiveReturnCode = process.returncode
	if archiveReturnCode != 0:
		print "archive workspace %s failed" %(workspace)
		cleanArchiveFile(archivePath)
	else:
		exportDirectory = exportArchive(scheme, archivePath)
		cleanArchiveFile(archivePath)
		if exportDirectory != "":		
			ipaPath = getIpaPath(exportDirectory,scheme)
			uploadIpaToPgyer(ipaPath)

def xcbuild(options):
	project = options.project
	workspace = options.workspace
	scheme = options.scheme

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

	options = parser.parse_args()

	print "options: %s" % (options)

	xcbuild(options)

if __name__ == '__main__':
	main()
