"""Builds p-keystone-qcom sdm845 on a Busytown build host.
"""

import build_busytown

build_busytown.build_target('cuttlestone_x86_phone', 'userdebug')
