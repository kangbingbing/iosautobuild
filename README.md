# iosautobuild
ios 打包脚本

#### 20230920 更新：
* 升级 Python3.x
* 更换蒲公英最新上传API

升级xocde9之后, 自动打包脚本需要做些更新.

exportOptions.plist
增加指定描述文件, key为bundleid，value为描述文件名称

	<key>provisioningProfiles</key>
		<dict>
			<key>com.ruanrong.hjzgiosapp</key>
			<string>hjztadhoc</string>
		</dict>


使用方法，把 autobuild 文件夹放到项目根目录，终端 cd 到 autobuild， 执行 bash t.sh 即可。 （t.sh需把 HJZG 更换成您的项目名）

或者执行 python autobuild.py -w ../schemename.xcworkspace -s schemename。 schemename即项目的schemename





[参考资料 http://liumh.com/2015/11/25/ios-auto-archive-ipa/](http://liumh.com/2015/11/25/ios-auto-archive-ipa/)
