import os, yaml, uuid, logging, time
from aiohttp import web
from homeassistant.components.http import HomeAssistantView
import homeassistant.config as conf_util

from .api_config import ApiConfig

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'ha_sidebar'
VERSION = '1.0'
URL = '/ha_sidebar-api'
ROOT_PATH = '/ha_sidebar-local/' + VERSION
StorageFile = 'ha_sidebar.json'

def setup(hass, config):
    cfg  = config[DOMAIN]
    sidebar_title = cfg.get('sidebar_title', '侧边栏管理')
    sidebar_icon = cfg.get('sidebar_icon', 'mdi:xbox-controller-menu')
    

    # 注册静态目录
    local = hass.config.path("custom_components/" + DOMAIN + "/local")
    if os.path.isdir(local):
        hass.http.register_static_path(ROOT_PATH, local, False)

        hass.components.frontend.async_register_built_in_panel(
            "iframe",
            sidebar_title,
            sidebar_icon,
            DOMAIN,
            {"url": ROOT_PATH + "/index.html?ver=" + VERSION},
            require_admin=True)

    hass.http.register_view(HassGateView)

    api = ApiConfig(hass.config.path('./.storage'))
    hass.data[DOMAIN] = api
    _list = api.read(StorageFile)
    if _list is not None:
        for item in _list:
            hass.components.frontend.async_register_built_in_panel(
                "iframe",
                item['name'],
                item['icon'],
                item['path'],
                {"url": ROOT_PATH + '/link.html?mode=' + str(item['mode']) +'&link=' + item['link']},
                require_admin=True)
    # 显示插件信息
    _LOGGER.info('''
-------------------------------------------------------------------
    侧边栏管理【作者QQ：635147515】
    
    版本：''' + VERSION + '''    
        
    项目地址：https://github.com/shaonianzhentan/ha_sidebar
-------------------------------------------------------------------''')
    return True


class HassGateView(HomeAssistantView):

    url = URL
    name = DOMAIN
    requires_auth = True
        
    async def post(self, request):
        hass = request.app["hass"]
        try:
            api = hass.data[DOMAIN]
            _list = api.read(StorageFile)
            if _list is None:
                _list = []
            query = await request.json()
            _type = query['type']
            if _type == 'get':
                return self.json({'code':0, 'msg': '查询成功', 'data': _list})
            elif _type == 'add':
                _path = '_' + str(time.time())
                # 添加所有菜单
                hass.components.frontend.async_register_built_in_panel(
                            "iframe",
                            query['name'],
                            query['icon'],
                            _path,
                            {"url": ROOT_PATH + '/link.html?mode=' + str(query['mode']) +'&link=' + query['link']},
                            require_admin=True)
                # 添加数据
                _list.append({
                    'name': query['name'],
                    'icon': query['icon'],
                    'link': query['link'],
                    'mode': query['mode'],
                    'path': _path,
                })
                api.write(StorageFile, _list)
                return self.json({'code':0, 'msg': '保存成功'})
            elif _type == 'delete':
                panel = hass.data.get("frontend_panels", {})
                _path = query['path']
                if _path in panel:
                    hass.components.frontend.async_remove_panel(_path)
                for i in range(len(_list)):
                    if _list[i]['path'] == _path:
                        # 删除数据，保存文件
                        del _list[i]
                        api.write(StorageFile, _list)
                        return self.json({'code':0, 'msg': '删除成功'})
                return self.json({'code':0, 'msg': '数据不存在'})
            elif _type == 'edit':
                _path = query['path']
                for i in range(len(_list)):
                    if _list[i]['path'] == _path:
                        _list[i]['name'] = query['name']
                        _list[i]['icon'] = query['icon']
                        _list[i]['link'] = query['link']
                        _list[i]['mode'] = query['mode']
                        hass.components.frontend.async_register_built_in_panel(
                            "iframe",
                            query['name'],
                            query['icon'],
                            _path,
                            {"url": ROOT_PATH + '/link.html?mode=' + str(query['mode']) +'&link=' + query['link']},
                            require_admin=True)

                api.write(StorageFile, _list)
                return self.json({'code':0, 'msg': '保存成功'})
        except Exception as e:
            _LOGGER.error(e)
            return self.json({'code':1, 'msg': '出现异常'})