
class ApiSidebar():

    def __init__(self, hass, cfg):
        self.hass = hass
        self.tabs_name = cfg.get('tabs_name', '二级菜单')
        self.tabs_icon = cfg.get('tabs_icon', 'mdi:format-list-numbered')

    @property
    def panel(self):
        return self.hass.data.get("frontend_panels", {})

    def remove(self, _path):
        if _path in self.panel:
            self.hass.components.frontend.async_remove_panel(_path)

    def add_tabs(self, ROOT_PATH, VERSION):
        self.add(self.tabs_name, self.tabs_icon, "ha_sidebar-tabs", ROOT_PATH + '/tabs.html?ver=' + VERSION)

    def add(self, name, icon, _path, url):
        self.hass.components.frontend.async_register_built_in_panel(
                        "iframe",
                        name,
                        icon,
                        _path,
                        {"url": url},
                        require_admin=True)