from setuptools import setup

package_name = "battery_manager"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="EdgeFleet Team",
    maintainer_email="team@edgefleet.dev",
    description="Battery simulation for EdgeFleet AMRs",
    license="MIT",
    entry_points={
        "console_scripts": [
            "battery_node = battery_manager.battery_node:main",
        ],
    },
)
