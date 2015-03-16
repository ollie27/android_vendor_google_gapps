# android_vendor_google_gapps

A simple way to add google apps to an android build.
  1. Copy gapps to ```proprietary/system/```
  2. Run ```$ ./createmk.py```
  3. Add ```$(call inherit-product, vendor/google/gapps/gapps.mk)``` to one of your device's mk files
