import { call } from './service.js'

export function getMenus() {
    return call("FlrMenu", "get_menus");
}

export function getViews(menuId) {
    return call("FlrView", "read", [["model","definition","view_type"]],
        {filters: [['menu_id','=',menuId]], order: "sequence"})
}