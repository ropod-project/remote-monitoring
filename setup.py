from setuptools import setup, find_packages

setup(name='remote_monitoring',
      version='1.0.0',
      description='A robot remote monitoring library',
      url='git@git.ropod.org:ropod/execution-monitoring/remote-monitoring.git',
      author='Alex Mitrevski, Santosh Thoduka',
      author_email='aleksandar.mitrevski@h-brs.de, santosh.thoduka@h-brs.de',
      keywords='remote_monitoring fault_detection robotics',
      packages=find_packages(exclude=['contrib', 'docs', 'tests']),
      project_urls={
          'Source': 'https://github.com/ropod-project/component-monitoring'
      })
