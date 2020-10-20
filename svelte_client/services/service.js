import { writable } from 'svelte/store';
import { get_store_value } from 'svelte/internal'

if(localStorage.getItem("flare_yourappname_jwt")){
    var initial_jwt = localStorage.getItem("flare_yourappname_jwt");
}else{
    var initial_jwt = "";
}

export const jwt = writable(initial_jwt);
export const loading = writable(false);

export function get_jwt_token(){
    return get_store_value(jwt);
}

export function auth(login, password){
    loading.set(true);
    return fetch('/auth', {
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify({
            login: login,
            password: password
        })
    })
    .then(function(resp) {
        return resp.json();
    })
    .catch((data) => {
        alert('Error');
    })
    .then(
        (resp) => {
            if(resp.result){
                jwt.set(resp.result);
                localStorage.setItem("flare_yourappname_jwt", resp.result);
            }
            loading.set(false);
            return resp;
        }
    )
}

export function call(model, method, args, kwargs){
    loading.set(true);
    return fetch("/call", {
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + get_store_value(jwt)
        },
        method: 'POST',
        body: JSON.stringify({
            'model': model,
            'method': method,
            'args': args,
            'kwargs': kwargs
        })
    })
    .then(async function(_resp) {
        loading.set(false);
        var resp = await _resp.json();
        if(resp.error){
            alert(resp.error.message);
            return resp;
        }else{
            return resp.result;
        }
    })
    .catch((data) => {
        alert("Error");
    })
}