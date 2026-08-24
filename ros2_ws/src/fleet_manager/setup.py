from setuptools import setup
import os
from glob import glob

package_name = "fleet_manager"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="EdgeFleet Team",
    maintainer_email="team@edgefleet.dev",
    description="Central fleet coordination for EdgeFleet",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "fleet_manager_node = fleet_manager.fleet_manager_node:main",
        ],
    },
)
