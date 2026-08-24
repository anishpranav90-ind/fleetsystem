from setuptools import setup

package_name = "task_allocator"

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
    description="Task allocation for EdgeFleet multi-robot system",
    license="MIT",
    entry_points={
        "console_scripts": [
            "task_allocator_node = task_allocator.task_allocator_node:main",
        ],
    },
)
