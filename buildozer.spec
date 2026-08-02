[app]
title = HCTL
package.name = hctl
package.domain = com.floppaos.hctl

source.dir = .
source.include_exts = py,png,jpg,kv,atlas
source.exclude_exts = spec

version = 1.0.0

requirements = kivy==2.3.0,python-dateutil,pyjnius,android

orientation = portrait

osx.frameworks = 

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 31
android.minapi = 26
android.ndk = 25b
android.accept_any_license = True

[buildozer]
log_level = 2
warn_on_root = 1
