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
from django.core.management.base import BaseCommand
from django.template import Context, Template

from bkuser_shell.version_log.utils import get_version_list

CHANGE_MD_TMPL = Template(
    """<!-- generated by script, do not modify it manually -->
# Changelog [{{ version.version }}] - {{ version.date }} 
{% for change_log in version.changeLogs %}
{% if change_log.project != '__Global__' %}## {{ change_log.project }}{% endif %}
{% for detail in change_log.detail %}
### {{ detail.type }}
{% for item in detail.content %}
- {{ item }}{% endfor %}
{% endfor %}{% endfor %}
"""  # noqa
)

ENTRY_MD_TMPL = Template(
    """<!-- generated by script, do not modify it manually -->
# CHANGELOGs
{% for entry in entries %}
- [{{ entry.name }}]({{ entry.path }}){% endfor %}
"""  # noqa
)


class Command(BaseCommand):
    help = "refresh profiles extras format"

    def handle(self, *args, **options):
        entries = []
        for version in get_version_list().versions:
            content = CHANGE_MD_TMPL.render(Context({"version": version}))

            entry = f"changelogs/CHANGELOG-{version.version}.md"
            with open(entry, "w") as f:
                f.write(content)

            entries.append({"name": f"CHANGELOG-{version.version}.md", "path": entry})

        with open("release.md", "w") as f:
            f.write(ENTRY_MD_TMPL.render(Context({"entries": entries})))
