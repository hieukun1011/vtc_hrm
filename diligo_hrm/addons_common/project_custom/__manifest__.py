# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "Project custom",
  "summary"              :  """Project custom""",
  "category"             :  "Project",
  "version"              :  "",
  "sequence"             :  1,
  "author"               :  "Quangnh",
  "license"              :  "",
  "website"              :  "",
  "description"          :  """""",
  "live_test_url"        :  "",
  "depends"              :  ['project', 'project_task_timer', 'diligo_hr',"hr"], #project_task_timer
  "data"                 :  [
      "security/ir.model.access.csv",
      'views/project_task_inherit.xml',
      'views/hr_employee_kanban_view_inherit.xml',
      'wizard/project_task_send_mail.xml',
      # 'demo/demo_data.xml',
                            ],
  'demo': [],
  "assets": {
        'web.assets_backend': [
            'project_custom/static/src/css/project_backend.css',
        ],
    },
    "images": [],
    "application": False,
    "installable": True,
    "auto_install": False,
    "price": 49,

}
