"""Builds msm8917 on an Busytown build host.
"""

import build_busytown

build_goals = [
    'TEMPORARY_DISABLE_PATH_RESTRICTIONS=true', '-k'
]

build_busytown.build_target_custom('msm8937_32go', 'userdebug', build_goals)
