from core.celery import app
from core.models.Mail.Mail import Mail, RedisQMail
from .EnqueueMailToActiveChannels import EnqueueMailToActiveChannels
from core.tasks.BaseTasks.BaseTask import BaseTask
from core.tasks.ESI.CharacterPublicInfo import CharacterPublicInfo
from core.tasks.ESI.CorporationInfo import CorporationInfo
from core.tasks.ESI.AllianceInfo import AllianceInfo
from core.tasks.ESI.SystemInfo import SystemInfo
from core.tasks.ESI.ConstellationInfo import ConstellationInfo
from core.tasks.ESI.RegionInfo import RegionInfo
from core.tasks.ESI.TypeInfo import TypeInfo
from core.tasks.ESI.GroupInfo import GroupInfo
from core.tasks.ESI.CategoryInfo import CategoryInfo


@app.task(base=BaseTask, bind=True, max_retries=10, default_retry_delay=5, autoretry_for=(Exception,))
def ProcessMailLoadFromESI(self, mail_json) -> None:
    """Enqueue all ESI calls to resolve data that isn't present from ZK.

    :param self: Celery self reference required for retries.
    :param mail_json: json dictionary containing RedisQ ZK data.
    :type mail_json: dict
    :rtype: None
    """
    m = Mail.from_json(RedisQMail.from_json(mail_json).to_json())
    r = ProcessMailLoadFromESI.redis

    if m.system_id:
        esi = SystemInfo.get_cached(r, system_id=m.system_id)
        m.system_name = esi
        m.system_security_status = esi
        m.system_pos_x = esi
        m.system_pos_y = esi
        m.system_pos_z = esi
        m.constellation_id = esi
        esi = ConstellationInfo.get_cached(r, constellation_id=m.constellation_id)
        m.constellation_name = esi
        m.region_id = esi
        esi = RegionInfo.get_cached(r, region_id=m.region_id)
        m.region_name = esi

    if m.victim:
        if m.victim.character_id:
            esi = CharacterPublicInfo.get_cached(r, character_id=m.victim.character_id)
            m.victim.character_name = esi
        if m.victim.corporation_id:
            esi = CorporationInfo.get_cached(r, corporation_id=m.victim.corporation_id)
            m.victim.corporation_name = esi
        if m.victim.alliance_id:
            esi = AllianceInfo.get_cached(r, alliance_id=m.victim.alliance_id)
            m.victim.alliance_name = esi
        if m.victim.ship_type_id:
            esi = TypeInfo.get_cached(r, type_id=m.victim.ship_type_id)
            m.victim.ship_type_name = esi
            m.victim.ship_group_id = esi
            esi = GroupInfo.get_cached(r, group_id=m.victim.ship_group_id)
            m.victim.ship_group_name = esi
            m.victim.ship_category_id = esi
            esi = CategoryInfo.get_cached(r, category_id=m.victim.ship_category_id)
            m.victim.ship_category_name = esi

    for a in m.attackers:
        if a.character_id:
            esi = CharacterPublicInfo.get_cached(r, character_id=a.character_id)
            a.character_name = esi
        if a.corporation_id:
            esi = CorporationInfo.get_cached(r, corporation_id=a.corporation_id)
            a.corporation_name = esi
        if a.alliance_id:
            esi = AllianceInfo.get_cached(r, alliance_id=a.alliance_id)
            a.alliance_name = esi
        if a.ship_type_id:
            esi = TypeInfo.get_cached(r, type_id=a.ship_type_id)
            a.ship_type_name = esi
            a.ship_group_id = esi
            esi = GroupInfo.get_cached(r, group_id=a.ship_group_id)
            a.ship_group_name = esi
            a.ship_category_id = esi
            esi = CategoryInfo.get_cached(r, category_id=a.ship_category_id)
            a.ship_category_name = esi
        if a.weapon_type_id:
            esi = TypeInfo.get_cached(r, type_id=a.weapon_type_id)
            a.weapon_type_name = esi
            a.weapon_group_id = esi
            esi = GroupInfo.get_cached(r, group_id=a.weapon_group_id)
            a.weapon_group_name = esi
            a.weapon_category_id = esi
            esi = CategoryInfo.get_cached(r, category_id=a.weapon_category_id)
            a.weapon_category_name = esi

    EnqueueMailToActiveChannels.apply_async(kwargs={"mail_json": m.to_json()}, ignore_result=True)