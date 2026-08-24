from setuptools import setup

package_name = "path_planner"

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
    description="A* global path planner for EdgeFleet",
    license="MIT",
    entry_points={
        "console_scripts": [
            "path_planner_node = path_planner.path_planner_node:main",
        ],
    },
)
