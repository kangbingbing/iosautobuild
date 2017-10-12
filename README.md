# iosautobuild
ios 打包脚本

升级xocde9之后, 自动打包脚本需要做些更新.

exportOptions.plist
增加指定描述文件, key为bundleid value为描述文件名称
<key>provisioningProfiles</key>
	<dict>
		<key>com.ruanrong.hjzgiosapp</key>
		<string>hjztadhoc</string>
	</dict>

[参考资料 http://liumh.com/2015/11/25/ios-auto-archive-ipa/](http://liumh.com/2015/11/25/ios-auto-archive-ipa/)
