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
    'cuttlestone_x86_phone': ['cuttlestone'],
    'msmnile': ['qcom-LA.UM.7.1.r1-incoming'],
}

_CUTTLESTONE_FS_VIEW = [
    # Cuttlestone dependencies: Provides QC vendor extension HALs
    ("overlays/qcom-LA.UM.7.3-incoming/vendor/qcom/opensource/interfaces",
     "vendor/qcom/opensource/interfaces"),
    ("overlays/qcom-LA.UM.7.3-incoming/vendor/qcom/proprietary/interfaces",
     "vendor/qcom/proprietary/interfaces"),
    ("overlays/qcom-LA.UM.7.3-incoming/vendor/qcom/proprietary/commonsys-intf/telephony",
     "vendor/qcom/proprietary/commonsys-intf/telephony"),
    # Cuttlestone dependencies: Provides telephony-ext, ims-ext-common, and
    #     qtiNetworkLib, used by a variety of telephony services
    ("overlays/qcom-LA.UM.7.3-incoming/vendor/codeaurora/commonsys/telephony",
     "vendor/codeaurora/commonsys/telephony"),
    ("overlays/qcom-LA.UM.7.3-incoming/vendor/qcom/proprietary/commonsys/telephony-apps",
     "vendor/qcom/proprietary/commonsys/telephony-apps"),
    # Cuttlestone dependencies: Provides display headers used by SurfaceFlinger
    ("overlays/qcom-LA.UM.7.3-incoming/vendor/qcom/opensource/commonsys-intf/display",
     "vendor/qcom/opensource/commonsys-intf/display"),
    # Cuttlestone dependencies: Provides the tcmiface java library
    ("overlays/qcom-LA.UM.7.3-incoming/vendor/qcom/opensource/commonsys/dpm",
     "vendor/qcom/opensource/commonsys/dpm"),
    # Cuttlestone dependencies: Provides system Bluetooth components
    ("overlays/qcom-LA.UM.7.3-incoming/hardware/qcom/bt", "hardware/qcom/bt"),
    ("overlays/qcom-LA.UM.7.3-incoming/vendor/qcom/opensource/commonsys/bluetooth",
     "vendor/qcom/opensource/commonsys/bluetooth"),
    ("overlays/qcom-LA.UM.7.3-incoming/vendor/qcom/opensource/commonsys/bluetooth_ext",
     "vendor/qcom/opensource/commonsys/bluetooth_ext"),
    ("overlays/qcom-LA.UM.7.3-incoming/vendor/qcom/opensource/commonsys/system/bt",
     "vendor/qcom/opensource/commonsys/system/bt"),
    # Cuttlestone dependencies, Provides build scripts
    ("overlays/qcom-LA.UM.7.3-incoming/vendor/qcom/opensource/core-utils/build/vendor_hal_makefile_generator.sh",
     "device/qcom/common/vendor_hal_makefile_generator.sh"),
    ("overlays/qcom-LA.UM.7.3-incoming/vendor/qcom/opensource/core-utils/build/stop_scan.mk",
     "vendor/qcom/proprietary/commonsys/Android.mk"),
]

# A map (optionally) specifying a filesystem view mapping for each target.
# The value for each target is a set of (to, from) tuples, representing paths
# (relative to the Android build root) to map into the specified locations.
FS_VIEW_MAP = {
    'cuttlestone_x86_phone': _CUTTLESTONE_FS_VIEW,
}
