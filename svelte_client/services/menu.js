import { call } from './service.js'

export function getMenus() {
    return call("FlrMenu", "get_menus");
}

export function getViews(type) {
    let kwargs = {}
    if (typeof type === 'number'){
        kwargs.filters = [['menu_id','=',type]]
        kwargs.order = "sequence"
    }
    if (typeof type === 'string'){
        kwargs.filters = [['model','=',type]]
    }
    return call("FlrView", "read", [
        ["model","definition","view_type","menu_id","name"]], kwargs)
}