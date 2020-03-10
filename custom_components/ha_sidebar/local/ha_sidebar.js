(() => {
    setInterval(() => {
        let menu = localStorage['ha_sidebar_hide_menu']
        if (menu) {
            try {
                menu = JSON.parse(menu)
                document.querySelector("home-assistant")
                    .shadowRoot.querySelector("home-assistant-main")
                    .shadowRoot.querySelector("app-drawer-layout app-drawer ha-sidebar")
                    .shadowRoot.querySelectorAll("paper-listbox a").forEach(ele => {
                        if (ele.pathname in menu) {
                            let isHide = menu[ele.pathname]
                            ele.style.display = isHide ? 'none' : 'block'
                        }
                    })
            } catch (ex) {
                localStorage.removeItem('ha_sidebar_hide_menu')
            }
        }
    }, 1000)
})();