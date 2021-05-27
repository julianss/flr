import { call, appTitle } from './service.js';
import { updateHash, replaceHash } from './../services/utils.js';
import { publish, globalsStore } from './writables.js';

export function getMenus() {
    return call("FlrMenu", "get_menus");
}

export function getViews(which, types) {
    let kwargs = {}
    if (typeof which === 'number'){
        kwargs.filters = [['menu_id','=',which]]
        kwargs.order = "sequence"
    }
    if (typeof which === 'string'){
        kwargs.filters = [['model','=',which]]
    }
    if(types){
        kwargs.filters.push(['view_type','in',types])
    }
    return call("FlrView", "read", [
        ["model","definition","view_type","menu_id","name","wizard","card_view_template","card_view_first"]], kwargs)
}

export function openViews(views, options={}){
    let loadedViews = {};
    let firstType = null;
    for(let view of views){
      loadedViews[view.view_type] = view;
      if (view.menu_id){
        loadedViews[view.view_type]['menu_view_name'] = view.menu_id.name;
        document.title =  appTitle.concat(' - ', view.menu_id.name);
      }
      else {
        loadedViews[view.view_type]['menu_view_name'] = view.name;
        document.title = appTitle.concat(' - ', view.name);
      }
      if(firstType === null && view.view_type != "search"){
        firstType = view.view_type;
      }
      if(view.view_type == "form"){
        if(options.asWizard === true){
          view.wizard = true;
        }
        if(options.showSaveButton === true){
          view.showSaveButton = true
        }
        if(options.reloadOnSave === true){
          view.reloadOnSave = true
        }
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

export function clickMenu(menuId, type, id) {
    if(menuId){
      globalsStore.set({})
      getViews(menuId).then(
        (resp) => {
          openViews(resp);
          if(type == 'form' && id){
            updateHash({
              menu_id: menuId,
              type: 'form',
              id: id
            })
            publish({
              event: 'activeViewChanged',
              type: 'form'
            })
            publish({
              event: 'activeRecordIdChanged',
              id: parseInt(id)
            })
          }else{
            replaceHash({menu_id: menuId})
          }
        }
      )
    }
  }