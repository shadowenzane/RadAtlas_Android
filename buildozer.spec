[app]

title = RadAtlas 影像图鉴助手
package.name = radatlas
package.domain = org.radatlas
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db,json
requirements = python3,kivy,sqlite3
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.archs = arm64-v8a,armeabi-v7a
android.allow_backup = True
android.logcat_filters = *:S python:D
android.storage_preset = internal
p4a.branch = master

[buildozer]

log_level = 2
warn_on_root = 1
build_dir = ./.buildozer
bin_dir = ./bin
