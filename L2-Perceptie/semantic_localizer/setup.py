from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'semantic_localizer'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Bogdan Felician Abaza',
    maintainer_email='bogdan.abaza@upb.ro',
    description='ROS 2 package for persistent semantic object mapping, semantic graph annotation, and integration with Nav2 Route Server for semantic-aware indoor navigation experiments.',
    license='MIT',
    entry_points={
        'console_scripts': [
            'semantic_localizer_node = semantic_localizer.semantic_localizer_node:main',
        ],
    },
)
