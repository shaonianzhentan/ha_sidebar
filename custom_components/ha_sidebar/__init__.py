import os, yaml, uuid, logging, time, importlib
from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant import config as conf_util, loader
from urllib.parse import quote,unquote

from .api_config import ApiConfig
from .api_sidebar import ApiSidebar

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'ha_sidebar'
VERSION = '1.5.3'
URL = '/ha_sidebar-api-' + VERSION
ROOT_PATH = '/ha_sidebar-local/' + VERSION
StorageFile = 'ha_sidebar.json'

def setup(hass, config):
    cfg  = config[DOMAIN]
    sidebar_title = cfg.get('sidebar_title', '侧边栏管理')
    sidebar_icon = cfg.get('sidebar_icon', 'mdi:xbox-controller-menu')
    api = ApiConfig(hass.config.path('./.storage'))
    api.api_sidebar = ApiSidebar(hass, cfg)
    hass.data[DOMAIN] = api

    # 注册静态目录
    local = hass.config.path("custom_components/" + DOMAIN + "/local")
    if os.path.isdir(local):
        hass.http.register_static_path(ROOT_PATH, local, False)
        api.api_sidebar.add(sidebar_title, sidebar_icon, DOMAIN, ROOT_PATH + "/index.html?ver=" + VERSION)

    hass.http.register_view(HassGateView)

    _list = api.read(StorageFile)
    if _list is not None:
        for item in _list:
            if item['mode'] == '5':
                api.api_sidebar.add_tabs(ROOT_PATH, VERSION)
            else:
                api.api_sidebar.add(
                    item['name'],
                    item['icon'],
                    item['path'],
                    ROOT_PATH + '/link.html?mode=' + str(item['mode']) +'&link=' + quote(item['link'], 'utf-8'))
    
    if hass.services.has_service(DOMAIN, 'reload') == False:
        async def reload(call):
            integration = await loader.async_get_integration(hass, DOMAIN)
            component = integration.get_component()
            importlib.reload(component)
            config = await conf_util.async_hass_config_yaml(hass)
            component.setup(hass, config)

        hass.services.register(DOMAIN, 'reload', reload)
    # 注入定时脚本
    hass.components.frontend.add_extra_js_url(hass, ROOT_PATH + '/ha_sidebar.js')
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
            elif _type == 'get_tabs':
                res = list(filter(lambda x: x['mode'] == '5', _list))
                return self.json({'code':0, 'msg': '查询成功', 'data': res})
            elif _type == 'add':
                _path = '_' + str(time.time())
                mode = str(query['mode'])                
                if mode == '5':
                    api.api_sidebar.add_tabs(ROOT_PATH, VERSION)
                else:    
                    # 添加所有菜单
                    api.api_sidebar.add(query['name'], query['icon'], _path, ROOT_PATH + '/link.html?mode=' + mode +'&link=' + quote(query['link'],'utf-8'))
                # 添加数据
                _list.append({
                    'name': query['name'],
                    'icon': query['icon'],
                    'link': query['link'],
                    'mode': mode,
                    'path': _path,
                })
                api.write(StorageFile, _list)
                return self.json({'code':0, 'msg': '保存成功'})
            elif _type == 'delete':
                _path = query['path']
                api.api_sidebar.remove(_path)
                for i in range(len(_list)):
                    if _list[i]['path'] == _path:
                        # 删除数据，保存文件
                        del _list[i]
                        api.write(StorageFile, _list)
                        return self.json({'code':0, 'msg': '删除成功'})
                return self.json({'code':0, 'msg': '数据不存在'})
            elif _type == 'edit':
                _path = query['path']
                mode = str(query['mode'])
                if mode == '5':
                    api.api_sidebar.remove(_path)
                    api.api_sidebar.add_tabs(ROOT_PATH, VERSION)

                for i in range(len(_list)):
                    if _list[i]['path'] == _path:
                        _list[i]['name'] = query['name']
                        _list[i]['icon'] = query['icon']
                        _list[i]['link'] = query['link']
                        _list[i]['mode'] = mode
                        if mode != '5':
                            api.api_sidebar.add(query['name'],query['icon'],_path,ROOT_PATH + '/link.html?mode=' + mode +'&link=' + quote(query['link'], 'utf-8'))

                api.write(StorageFile, _list)
                return self.json({'code':0, 'msg': '保存成功'})
            elif _type == 'reload':
                integration = await loader.async_get_integration(hass, DOMAIN)
                component = integration.get_component()
                importlib.reload(component)
                config = await conf_util.async_hass_config_yaml(hass)
                component.setup(hass, config)
                return self.json({'code':0, 'msg': '保存成功'})
            elif _type == 'update':
                _path =  hass.config.path("custom_components").replace('\\','/')
                _sh =  _path+'/ha_sidebar/update.sh'
                with open(_sh, 'r', encoding='utf-8') as f:
                    content = f.read().replace('$source_path', _path)
                with open(_sh, 'w', encoding='utf-8') as f:
                    f.write(content)
                os.system(_sh)
                return self.json({'code':0, 'msg': '升级成功'})
        except Exception as e:
            _LOGGER.error(e)
            return self.json({'code':1, 'msg': '出现异常'})