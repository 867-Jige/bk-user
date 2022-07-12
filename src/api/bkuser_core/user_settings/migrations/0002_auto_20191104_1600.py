# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-用户管理(Bk-User) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
# Generated by Django 1.11.23 on 2019-11-04 16:00
from __future__ import unicode_literals

from django.db import migrations

from bkuser_core.categories.constants import CategoryType
from bkuser_core.user_settings.constants import SettingsEnableNamespaces


def forwards_func(apps, schema_editor):
    """添加默认用户目录"""
    SettingMeta = apps.get_model("user_settings", "SettingMeta")

    local_password_settings = [
        dict(key="password_min_length", example=8, default=8),
        dict(
            key="password_must_includes",
            example=["upper", "lower", "int"],
            default=["upper", "lower", "int"],
        ),
        dict(key="password_valid_days", example=30, default=30),
        dict(key="max_trail_times", example=3, default=3),
        dict(key="auto_unlock_seconds", example=600, default=600),
        dict(
            key="init_password_method",
            choices=["fixed_preset", "random_via_mail"],
            default="fixed_preset",
        ),
        dict(
            key="init_password",
            example="bk@Ctb3mR7GHNAvUVQW",
            default="bk@Ctb3mR7GHNAvUVQW",
        ),
        dict(
            key="init_mail_config",
            default={
                "title": "蓝鲸智云 - 您的账户已经成功创建！",
                "sender": "蓝鲸智云",
                "content": "您好！您的蓝鲸智云账户已经成功创建，以下是您的账户信息:登录账户：{username}， "
                "初始登录密码：{password} 为了保障账户安全，我们建议您尽快登录蓝鲸智云修改密码：{url} "
                "此邮件为系统自动发送，请勿回复。蓝鲸智云官网： http://bk.tencent.com",
            },
        ),
        dict(
            key="reset_mail_config",
            default={
                "title": "蓝鲸智云 - 登录密码重置",
                "sender": "蓝鲸智云",
                "content": "您好！我们收到了你重置密码的申请，请点击下方链接进行密码重置：{url} "
                "该链接有效时间为3小时，过期后请重新点击密码重置链接：{reset_url} 此邮件为系统自动发送，请勿回复",
            },
        ),
        dict(key="force_reset_first_login", example=True, default=True),
        dict(key="enable_auto_freeze", example=False, default=False),
        dict(key="freeze_after_days", example=180, default=180),
    ]

    for x in local_password_settings:
        SettingMeta.objects.create(
            namespace=SettingsEnableNamespaces.PASSWORD.value,
            category_type=CategoryType.LOCAL.value,
            required=True,
            **x
        )

    mad_connection_settings = [
        dict(
            key="connection_url",
            example="ldap://localhost:389",
            default="ldap://localhost:389",
        ),
        dict(key="ssl_encryption", choices=["无", "SSL"], default="无"),
        dict(key="timeout_setting", example=120, default=120),
        dict(key="pull_cycle", example=60, default=60),
        dict(key="base_dn", example="CN"),
        dict(key="user", example="user"),
        dict(key="password", example="password"),
    ]

    for x in mad_connection_settings:
        SettingMeta.objects.create(
            namespace=SettingsEnableNamespaces.CONNECTION.value,
            category_type=CategoryType.MAD.value,
            required=True,
            **x
        )

    basic_fields_connection_settings = [
        dict(key="basic_pull_node", choices=[]),
        dict(key="user_class", example="user", default="user"),
        dict(
            key="user_filter",
            example="(&(objectCategory=Person)(sAMAccountName=*))",
            default="(&(objectCategory=Person)(sAMAccountName=*))",
        ),
        dict(
            key="organization_class",
            example="organizationalUnit",
            default="organizationalUnit",
        ),
        dict(key="username", default="sAMAccountName"),
        dict(key="display_name", example="displayName", default="displayName"),
        dict(key="email", example="mail", default="mail"),
        dict(key="telephone", example="Telephone", default=""),
    ]

    for x in basic_fields_connection_settings:
        SettingMeta.objects.create(
            namespace=SettingsEnableNamespaces.FIELDS.value,
            category_type=CategoryType.MAD.value,
            required=True,
            region="basic",
            **x
        )

    extend_fields_connection_settings = [
        dict(key="bk_fields", choices=["职务", "性别", "年龄", "工作年限", "婚姻状态", "籍贯"]),
        dict(key="mad_fields", choices=["job", "gender", "age", "year", "marry", "home"]),
    ]

    for x in extend_fields_connection_settings:
        SettingMeta.objects.create(
            namespace=SettingsEnableNamespaces.FIELDS.value,
            category_type=CategoryType.MAD.value,
            required=True,
            region="extend",
            **x
        )

    group_fields_connection_settings = [
        dict(
            key="user_group_class",
            example="groupOfUniqueNames",
            default="groupOfUniqueNames",
        ),
        dict(
            key="user_group_filter",
            example="(objectclass=groupOfUniqueNames)",
            default="(objectclass=groupOfUniqueNames)",
        ),
        dict(
            key="user_group_name",
            example="cn",
            default="cn",
        ),
        dict(
            key="user_group_description",
            example="description",
            default="description",
        ),
    ]

    for x in group_fields_connection_settings:
        SettingMeta.objects.create(
            namespace=SettingsEnableNamespaces.FIELDS.value,
            category_type=CategoryType.MAD.value,
            required=True,
            region="group",
            **x
        )


class Migration(migrations.Migration):

    dependencies = [
        ("user_settings", "0001_initial"),
    ]

    operations = [migrations.RunPython(forwards_func)]
