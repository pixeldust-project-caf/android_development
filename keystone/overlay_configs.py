"""Defines overlay configuration for keystone builds.

Keep the overlay configuration information in a separate file for easier
tracking.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

OVERLAY_MAP = {
    'sdm845': ['qcom-LA.UM.7.3-incoming'],
    'sdm845_gms': ['qcom-LA.UM.7.3-incoming', 'gms'],
    'sdm660_64': ['qcom-LA.UM.7.2-incoming'],
}
