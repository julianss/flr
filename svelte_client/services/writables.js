import { writable } from 'svelte/store';
import { get_store_value } from 'svelte/internal'

export const viewsStore = writable(null);
export const activeRecordIdStore = writable();
export const activeViewStore = writable(null);
export const recordCreatedStore = writable(null);
export const searchFiltersStore = writable({});

export function publish(event) {
    event.timestamp = (new Date()).getTime();
    if(event.event == "viewsChanged"){
        viewsStore.set(event)
    }
    else if(event.event == "activeRecordIdChanged"){
        activeRecordIdStore.set(event);
    }
    else if(event.event == "activeViewChanged"){
        activeViewStore.set(event);
    }else if(event.event == "recordCreated"){
        recordCreatedStore.set(event);
    }else if(event.event == "filtersChanged"){
        searchFiltersStore.set(event);
    }
}

export function getValue(store){
    return get_store_value(store);
}