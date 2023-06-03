from distutils.core import setup

from setuptools import find_namespace_packages

setup(name='iflygpt',
      version='1.0',
      description='讯飞星火认知大模型 API',
      author='doublewinter0',
      author_email='erdong.me@gmail.com',
      url='https://www.github.com/doublewinter0/xfyun-xinghuo',
      license='GNU General Public License v3.0',
      packages=find_namespace_packages('src'),
      package_dir={'': 'src'},
      install_requires=[
          'httpx[socks]'
      ]
      )
