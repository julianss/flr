import { call } from './service.js'
import { publish } from './writables.js';

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

export function openViews(views){
    let loadedViews = {};
    let firstType = null;
    for(let view of views){
      loadedViews[view.view_type] = view;
      if (view.menu_id){
        loadedViews[view.view_type]['menu_view_name'] = view.menu_id.name;
      }
      else {
        loadedViews[view.view_type]['menu_view_name'] = view.name;
      }
      if(firstType === null && view.view_type != "search"){
        firstType = view.view_type;
      }
    }
    publish({
      event: 'viewsChanged',
      views: loadedViews,
    });
    publish({
      event: 'activeRecordIdChanged',
      id: null,
    })
    publish({
      event: 'activeViewChanged',
      type: firstType,
    })
  }