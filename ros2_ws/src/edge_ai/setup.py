from setuptools import setup

package_name = "edge_ai"

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
    description="Edge-AI local decision engine for EdgeFleet AMRs",
    license="MIT",
    entry_points={
        "console_scripts": [
            "edge_ai_node = edge_ai.edge_ai_node:main",
        ],
    },
)
