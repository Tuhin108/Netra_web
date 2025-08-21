[app]
title = Netra
package.name = netra
package.domain = org.example
source.dir = ..
source.include_exts = py,png,jpg,kv,atlas,txt
version = 0.1
requirements = python3,kivy,httpx,tldextract,rapidfuzz,beautifulsoup4,certifi,pyjnius
orientation = portrait
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/presplash.png
fullscreen = 0

android.permissions = INTERNET
android.api = 31
android.minapi = 21
android.sdk = 24
android.ndk = 19b

# Android intent filters
android.manifest.intent_filters = assets/intent_filters.xml

[buildozer]
log_level = 2
warn_on_root = 1
