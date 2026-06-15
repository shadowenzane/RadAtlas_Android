"""RadAtlas Android - 医学影像图鉴助手
楚雄州人民医院 医学影像中心 张兴文
"""
import sys
import os

# 确保 core/ 和 ui/ 在路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app import RadAtlasApp


def main():
    RadAtlasApp().run()


if __name__ == '__main__':
    main()
