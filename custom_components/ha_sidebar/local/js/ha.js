class HA {

    constructor() {
        let query = new URLSearchParams(location.search)
        this.query = key => {
            let val = query.get(key)
            if (val) {
                return decodeURIComponent(val)
            }
            return val
        }

        this.ver = this.query('ver')
        let hs = top.document.querySelector('home-assistant')
        if (hs) this.hass = hs.hass
    }

    fullscreen(mode = 0) {
        try {
            let haPanelIframe = top.document.body
                .querySelector("home-assistant")
                .shadowRoot.querySelector("home-assistant-main")
                .shadowRoot.querySelector("app-drawer-layout partial-panel-resolver ha-panel-iframe").shadowRoot
            let ha_card = haPanelIframe.querySelector("iframe");
            ha_card.style.position = 'absolute'

            if (mode === 0) {
                haPanelIframe.querySelector('app-toolbar').style.display = 'none'
                ha_card.style.top = '0'
                ha_card.style.height = '100%'
            }
        } catch (ex) {
            console.log(ex)
        }
    }

    // 触发事件
    fire(type, data, ele = null) {
        const event = new top.Event(type, {
            bubbles: true,
            cancelable: false,
            composed: true
        });
        event.detail = data;
        if (!ele) {
            ele = top.document.querySelector("home-assistant")
                .shadowRoot.querySelector("home-assistant-main")
                .shadowRoot.querySelector("app-drawer-layout")
        }
        ele.dispatchEvent(event);
    }

    // 提示
    toast(message) {
        this.fire("hass-notification", { message })
    }

    // 请求接口
    fetchApi(params) {
        return this.hass.fetchWithAuth('/ha_sidebar-api', {
            method: 'POST',
            body: JSON.stringify(params)
        }).then(res => res.json())
    }

    sandbox() {
        try {
            let iframe = top.document.querySelector("home-assistant")
                .shadowRoot.querySelector("home-assistant-main")
                .shadowRoot.querySelector("ha-panel-iframe").shadowRoot.querySelector("iframe")
            iframe.removeAttribute('sandbox')
            iframe.contentWindow.confirm = function (msg) { return top.confirm(msg) }
            iframe.contentWindow.alert = function (msg) { top.alert(msg) }
        } catch (ex) {
            console.log(ex)
        }
    }
}

window.ha = new HA()

var _hmt = _hmt || []; window._hmt = _hmt; (function () { var hm = document.createElement('script'); hm.src = 'https://hm.baidu.com/hm.js?52d57d8b7588a022f89c451d06e311f0'; var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(hm, s) })();