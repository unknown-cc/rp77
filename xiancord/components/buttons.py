from discord import Interaction , ButtonStyle
from ..logger import terminal
buttons_maps = {}

def register_button(callback_id):
    def decorater(func):
        buttons_maps[callback_id] = func
        return func
    return decorater

BUTTON_STYLE_MAP_CN = {
    "藍色": ButtonStyle.primary,
    "灰色": ButtonStyle.secondary,
    "綠色": ButtonStyle.success,
    "紅色": ButtonStyle.danger,
    "連結": ButtonStyle.link,
    "無": None,  # 不指定 style
}