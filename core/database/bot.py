from amiyabot import AmiyaBot, KOOKBotInstance
from amiyabot.database import *
from core.config import cos_config, penetration_config
from core.database import config, is_mysql
from core.cosChainBuilder import COSQQGroupChainBuilder
from typing import Union

from amiyabot.adapters.tencent.qqGuild import qq_guild_shards
from amiyabot.adapters.tencent.qqGlobal import qq_global
from amiyabot.adapters.tencent.qqGroup import qq_group, QQGroupChainBuilder, QQGroupChainBuilderOptions
from amiyabot.adapters.cqhttp import cq_http
from amiyabot.adapters.mirai import mirai_api_http
from amiyabot.adapters.onebot.v11 import onebot11
from amiyabot.adapters.onebot.v12 import onebot12
from amiyabot.adapters.comwechat import com_wechat
from amiyabot.adapters.test import test_instance

db = connect_database('amiya_bot' if is_mysql else 'database/amiya_bot.db', is_mysql, config)


class BotBaseModel(ModelClass):
    class Meta:
        database = db


@table
class Admin(BotBaseModel):
    account: Union[CharField, str] = CharField(unique=True)
    remark: Union[CharField, str] = CharField(null=True)

    @classmethod
    def is_super_admin(cls, user_id: str):
        return bool(cls.get_or_none(account=user_id))


@table
class BotAccounts(BotBaseModel):
    appid: str = CharField(unique=True)
    token: str = CharField()
    private: int = SmallIntegerField(default=0)
    is_start: int = SmallIntegerField(default=1)
    is_main: int = SmallIntegerField(default=0)
    console_channel: str = CharField(null=True)
    adapter: str = CharField(default='qq_guild')

    host: str = CharField(null=True)
    ws_port: int = IntegerField(null=True)
    http_port: int = IntegerField(null=True)
    client_secret: str = CharField(null=True)

    sandbox: int = SmallIntegerField(default=0)
    shard_index: int = SmallIntegerField(default=0)
    shards: int = SmallIntegerField(default=1)

    @classmethod
    def get_all_account(cls):
        select: List[cls] = cls.select()
        account = []

        for item in select:
            if not item.is_start:
                continue

            conf = cls.build_conf(item)
            account.append(AmiyaBot(**conf))

        return account

    @classmethod
    def build_conf(cls, item):
        net_adapters = {
            'mirai_api_http': mirai_api_http,
            'cq_http': cq_http,
            'onebot11': onebot11,
            'onebot12': onebot12,
            'com_wechat': com_wechat,
        }
        tx_adapters = {
            'qq_guild': qq_guild_shards,
            'qq_group': qq_group,
            'qq_global': qq_global,
        }

        conf = {
            'appid': item.appid,
            'token': item.token,
            'private': bool(item.private),
        }

        if item.adapter in net_adapters:
            conf['adapter'] = net_adapters[item.adapter](
                host=item.host,
                ws_port=item.ws_port,
                http_port=item.http_port,
            )

        if item.adapter in tx_adapters:
            adapter = tx_adapters[item.adapter]
            shards = {
                'shard_index': item.shard_index,
                'shards': item.shards,
            }
            if item.adapter == 'qq_guild':
                conf['adapter'] = adapter(**shards, sandbox=bool(item.sandbox))
            else:
                port = item.http_port or 8086
                opt = QQGroupChainBuilderOptions(item.host or '0.0.0.0', port, './resource/group_temp')

                if cos_config.activate:
                    conf['adapter'] = adapter(
                        item.client_secret,
                        default_chain_builder=COSQQGroupChainBuilder(opt),
                        **shards,
                    )
                else:

                    class PenetrationChainBuilder(QQGroupChainBuilder):
                        @property
                        def domain(self):
                            return (
                                penetration_config.ports[port] + '/resource'
                                if port in penetration_config.ports
                                else super().domain
                            )

                    cb = PenetrationChainBuilder(opt)

                    conf['adapter'] = adapter(item.client_secret, default_chain_builder=cb, **shards)

        if item.adapter == 'websocket':
            conf['adapter'] = test_instance(item.host, item.ws_port)

        if item.adapter == 'kook':
            conf['adapter'] = KOOKBotInstance

        return conf


@table
class FunctionUsed(BotBaseModel):
    function_id: str = CharField(primary_key=True)
    use_num: int = IntegerField(default=1)


@table
class DisabledFunction(BotBaseModel):
    function_id: str = CharField(null=True)
    channel_id: str = CharField(null=True)


@table
class OperatorIndex(BotBaseModel):
    name: Union[CharField, str] = CharField()
    en_name: Union[CharField, str] = CharField()
    rarity: Union[CharField, str] = CharField()
    classes: Union[CharField, str] = CharField()
    classes_sub: Union[CharField, str] = CharField()
    classes_code: Union[CharField, str] = CharField()
    type: Union[CharField, str] = CharField()


@table
class OperatorConfig(BotBaseModel):
    operator_name: str = CharField()
    operator_type: int = IntegerField()


@table
class Pool(BotBaseModel):
    pool_name: Union[CharField, str] = CharField(unique=True)

    pool_uuid: Union[CharField, str] = CharField(null=True, default='')
    '''
    用于区分同名非官方卡池，因为非官方卡池是可能会有同名的情况的
    而数字Id不适用于远端数据库
    '''
    
    pool_description: Union[CharField, str] = CharField(null=True, default='')
    '''
    卡池描述，为空或None时会根据卡池内容自动生成一个。
    '''

    pool_image: Union[CharField, str] = CharField(null=True, default='')
    '''
    卡池的题图
    '''

    limit_pool: int = IntegerField()
    '''
    卡池类型
    0: 常规寻访
    1: 限定寻访
    2: 联合寻访
    3: 前路回响
    4: 中坚寻访
    5: 其他寻访
    '''

    is_classicOnly: bool = BooleanField(default=False)
    '''
    填充干员是否只包含中坚干员
    '''
    is_official: bool = BooleanField(default=True)
    '''
    是否为官方卡池
    '''

    # 卡池Up干员，和Up干员的加总概率，设置为100即为联合寻访（只有Up干员）
    # 如果各个Up干员的rate不一样，可以在干员名后面用竖线分隔权重，权重可以为负数
    # 例如：'干员1|1,干员2|5,干员3|5'
    # 所有Up干员加权平分rate给出的概率。剩下的由常规干员填充
    # 概率为小数，大于1的概率值会被转换为1
    # 概率为None视为0
    # pickup_s 为 五倍权重提升的任意干员，或者1倍权重但是会在本池抽出的限定干员，注意：其他fillin干员，权重为1

    pickup_6: Union[CharField, str] = CharField(null=True, default='')
    pickup_6_rate: float = FloatField(null=True, default=None)
    pickup_s: Union[CharField, str] = CharField(null=True, default='')

    pickup_5: Union[CharField, str] = CharField(null=True, default='')
    pickup_5_rate: float = FloatField(null=True, default=None)
    pickup_s_5: Union[CharField, str] = CharField(null=True, default='')
    
    pickup_4: Union[CharField, str] = CharField(null=True, default='')
    pickup_4_rate: float = FloatField(null=True, default=None)
    pickup_s_4: Union[CharField, str] = CharField(null=True, default='')
    
    pickup_3: Union[CharField, str] = CharField(null=True, default='')
    pickup_3_rate: float = FloatField(null=True, default=None)
    pickup_s_3: Union[CharField, str] = CharField(null=True, default='')
    
    pickup_2: Union[CharField, str] = CharField(null=True, default='')
    pickup_2_rate: float = FloatField(null=True, default=0)
    pickup_s_2: Union[CharField, str] = CharField(null=True, default='')
    
    pickup_1: Union[CharField, str] = CharField(null=True, default='')
    pickup_1_rate: float = FloatField(null=True, default=0)
    pickup_s_1: Union[CharField, str] = CharField(null=True, default='')

    version: Union[CharField, str] = CharField(null=True, default='')


@table
class TextReplace(BotBaseModel):
    user_id: str = CharField()
    group_id: str = CharField()
    origin: Union[TextField, str] = TextField()
    replace: Union[TextField, str] = TextField()
    in_time: int = BigIntegerField()
    is_user_only: int = IntegerField(default=0)
    is_global: int = IntegerField(default=0)
    is_active: int = IntegerField(default=1)


@table
class TextReplaceSetting(BotBaseModel):
    text: str = CharField(unique=True)
    status: int = IntegerField()
