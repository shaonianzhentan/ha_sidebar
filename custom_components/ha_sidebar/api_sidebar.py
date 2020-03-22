
class ApiSidebar():

    def __init__(self, hass, cfg):
        self.hass = hass

    @property
    def panel(self):
        return self.hass.data.get("frontend_panels", {})

    def remove(self, _path):
        if _path in self.panel:
            self.hass.components.frontend.async_remove_panel(_path)

    def add(self, name, icon, _path, url):
        self.hass.components.frontend.async_register_built_in_panel(
                        "iframe",
                        name,
                        icon,
                        _path,
                        {"url": url},
                        require_admin=True)