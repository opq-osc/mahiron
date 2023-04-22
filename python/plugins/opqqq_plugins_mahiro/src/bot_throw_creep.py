import os
import random
from enum import Enum
from io import BytesIO

import httpx
from PIL import Image, ImageDraw

try:
    import ujson as json
except Exception:
    import json

from mahiro import GroupMessageMahiro

# ==========================================

RESOURCES_BASE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "resources", "throw-creep"
)

# ==========================================

# 屏蔽群 例：[12345678, 87654321]
blockGroupNumber = []
# 触发命令列表
creepCommandList = ["爬", "爪巴", "给爷爬", "爬啊", "快爬"]
throwCommandList = ["丢", "我丢"]
# 爬的概率 越大越容易爬 取值区间 [0, 100]
creep_limit = 80

# ==========================================


async def bot_throw_creep(mahiro: GroupMessageMahiro):
    ctx = mahiro.ctx
    is_text = mahiro.extra.is_text
    userGroup = ctx.groupId

    if Tools.commandMatch(userGroup, blockGroupNumber):
        return

    if not is_text:
        return

    ats = ctx.msg.AtUinLists
    if len(ats) != 1:
        return
    qq = ats[0].Uin
    msg = ctx.msg.Content.strip()

    # creep features
    result = Tools.commandMatch(msg, creepCommandList, model=Model.BLURRY)
    if result:
        outPath = ThrowAndCreep.creep(qq)
        mahiro.sender.send_to_group(group_id=userGroup, fast_image=outPath)
        return
    # throe features
    result = Tools.commandMatch(msg, throwCommandList, model=Model.BLURRY)
    if result:
        outPath = ThrowAndCreep.throw(qq)
        mahiro.sender.send_to_group(group_id=userGroup, fast_image=outPath)
        return


class Model(Enum):
    ALL = "_all"

    BLURRY = "_blurry"

    SEND_AT = "_send_at"

    SEND_DEFAULT = "_send_default"


class Status(Enum):
    SUCCESS = "_success"

    FAILURE = "_failure"


class Tools:
    @staticmethod
    def commandMatch(msg, commandList, model=Model.ALL):
        if model == Model.ALL:
            for c in commandList:
                if c == msg:
                    return True
        if model == Model.BLURRY:
            for c in commandList:
                if msg.find(c) != -1:
                    return True
        return False

    @staticmethod
    def checkFolder(dir):
        if not os.path.exists(dir):
            os.makedirs(dir)


class Network:
    @staticmethod
    def getBytes(url, headers="", timeout=10):
        if headers == "":
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
            }
        try:
            return httpx.get(url=url, headers=headers, timeout=timeout).read()
        except:
            return Status.FAILURE


class ThrowAndCreep:
    _avatar_size = 139

    _center_pos = (17, 180)

    @staticmethod
    def getAvatar(url):
        img = Network.getBytes(url)
        return img

    @staticmethod
    def randomClimb():
        randomNumber = random.randint(1, 100)
        if randomNumber < creep_limit:
            return True
        return False

    @staticmethod
    def get_circle_avatar(avatar, size):
        avatar.thumbnail((size, size))

        scale = 5
        mask = Image.new("L", (size * scale, size * scale), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size * scale, size * scale), fill=255)
        mask = mask.resize((size, size), Image.ANTIALIAS)

        ret_img = avatar.copy()
        ret_img.putalpha(mask)

        return ret_img

    @classmethod
    def creep(cls, qq):
        creeped_who = qq
        id = random.randint(0, 53)

        whetherToClimb = cls.randomClimb()

        if not whetherToClimb:
            return f"{RESOURCES_BASE_PATH}/不爬.jpg"

        avatar_img_url = "http://q1.qlogo.cn/g?b=qq&nk={QQ}&s=640".format(
            QQ=creeped_who
        )
        res = cls.getAvatar(avatar_img_url)
        avatar = Image.open(BytesIO(res)).convert("RGBA")
        avatar = cls.get_circle_avatar(avatar, 100)

        creep_img = Image.open(f"{RESOURCES_BASE_PATH}/pa/爬{id}.jpg").convert("RGBA")
        creep_img = creep_img.resize((500, 500), Image.ANTIALIAS)
        creep_img.paste(avatar, (0, 400, 100, 500), avatar)
        dirPath = f"{RESOURCES_BASE_PATH}/avatar"
        Tools.checkFolder(dirPath)
        creep_img.save(f"{RESOURCES_BASE_PATH}/avatar/{creeped_who}_creeped.png")

        return f"{RESOURCES_BASE_PATH}/avatar/{creeped_who}_creeped.png"

    @classmethod
    def throw(cls, qq):
        throwed_who = qq

        avatar_img_url = "http://q1.qlogo.cn/g?b=qq&nk={QQ}&s=640".format(
            QQ=throwed_who
        )

        res = cls.getAvatar(avatar_img_url)
        avatar = Image.open(BytesIO(res)).convert("RGBA")
        avatar = cls.get_circle_avatar(avatar, cls._avatar_size)

        rotate_angel = random.randrange(0, 360)

        throw_img = Image.open(f"{RESOURCES_BASE_PATH}/throw.jpg").convert("RGBA")
        throw_img.paste(
            avatar.rotate(rotate_angel), cls._center_pos, avatar.rotate(rotate_angel)
        )
        dirPath = f"{RESOURCES_BASE_PATH}/avatar"
        Tools.checkFolder(dirPath)
        throw_img.save(f"{RESOURCES_BASE_PATH}/avatar/{throwed_who}.png")

        return f"{RESOURCES_BASE_PATH}/avatar/{throwed_who}.png"
