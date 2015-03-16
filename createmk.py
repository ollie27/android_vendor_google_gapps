#!/usr/bin/env python

from __future__ import absolute_import, division, print_function, unicode_literals

import io
import os
import sys

PACKAGE_TYPES = [
    ("system/framework/", ".jar", "JAVA_LIBRARIES",
     ["LOCAL_MODULE_SUFFIX := $(COMMON_JAVA_PACKAGE_SUFFIX)"]),
    ("system/lib/", ".so", "SHARED_LIBRARIES",
     ["LOCAL_MODULE_SUFFIX := .so"]),
    ("system/app/", ".apk", "APPS",
     ["LOCAL_MODULE_SUFFIX := $(COMMON_ANDROID_PACKAGE_SUFFIX)",
      "LOCAL_CERTIFICATE := PRESIGNED"]),
    ("system/priv-app/", ".apk", "APPS",
     ["LOCAL_MODULE_SUFFIX := $(COMMON_ANDROID_PACKAGE_SUFFIX)",
      "LOCAL_CERTIFICATE := PRESIGNED",
      "LOCAL_PRIVILEGED_MODULE := true"]),
    ("system/etc/preferred-apps/", "", "ETC",
     ["LOCAL_MODULE_PATH := $(TARGET_OUT_ETC)/preferred-apps"]),
    ("system/etc/permissions/", "", "ETC",
     ["LOCAL_MODULE_PATH := $(TARGET_OUT_ETC)/permissions"]),
    ]

OVERRIDES = ["librsjni", "libRSSupport", "libjni_latinime"]

def main(path="proprietary", vendor="google", derp="gapps"):
    packages = []
    files = []
    copy_files = []
    to_write = []

    # with io.open('file list.txt', 'rt', encoding='utf-8') as f:
        # for x in f:
            # x = x.strip()
            # if x:
                # files.append(x)

    for root, dirs, fs in os.walk(path, topdown=False):
        for name in fs:
            files.append("{}/{}".format(root.replace("\\", "/"), name)[len(path) + 1:])

    to_write.append("LOCAL_PATH := $(call my-dir)")

    for f in sorted(files):
        print(f)
        is_package = False

        for path, suffix, module_class, custom_lines in PACKAGE_TYPES:
            if f.startswith(path) and f.endswith(suffix):
                name = f[len(path):-len(suffix) if len(suffix) > 0 else None]
                if name in OVERRIDES:
                    break
                is_package = True
                packages.append(name)
                to_write.append("")
                to_write.append("include $(CLEAR_VARS)")
                to_write.append("LOCAL_MODULE := {}".format(name))
                to_write.append("LOCAL_MODULE_TAGS := optional")
                to_write.append("LOCAL_SRC_FILES := proprietary/{}$(LOCAL_MODULE){}".format(path, suffix))
                to_write.append("LOCAL_MODULE_CLASS := {}".format(module_class))
                to_write.extend(custom_lines)
                to_write.append("include $(BUILD_PREBUILT)")
                break

        if not is_package:
            copy_files.append(f)

    with io.open('Android.mk', 'wt', encoding='utf-8') as f:
        f.writelines("{}\n".format(l) for l in to_write)

    to_write = []

    to_write.append("PRODUCT_PACKAGES += \\")
    for package in packages:
        to_write.append("    {} \\".format(package))

    to_write.append("")
    to_write.append("PRODUCT_COPY_FILES += \\")
    for f in copy_files:
        to_write.append("    vendor/{0}/{1}/proprietary/{2}:{2} \\".format(vendor, derp, f))

    with io.open('{}.mk'.format(derp), 'wt', encoding='utf-8') as f:
        f.writelines("{}\n".format(l) for l in to_write)

if __name__ == '__main__':
    main(*sys.argv[1:])
