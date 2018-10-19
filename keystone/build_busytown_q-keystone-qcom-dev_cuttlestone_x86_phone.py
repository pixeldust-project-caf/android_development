"""Builds q-keystone-qcom-dev cuttlestone_x86_phone on a Busytown build host.
"""

import build_busytown

build_busytown.build_target('cuttlestone_x86_phone', 'userdebug', extra_build_goals=['tests'])
