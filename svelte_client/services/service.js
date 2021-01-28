import { writable } from 'svelte/store';
import { get_store_value } from 'svelte/internal';
import { globalsStore } from './writables';

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
            'kwargs': kwargs,
            '$globals': get_store_value(globalsStore)
        })
    })
    .then(async function(_resp) {
        loading.set(false);
        var resp = await _resp.json();
        if(resp.error){
            alert(resp.error.message);
            resp.$error = resp.error;
            return resp;
        }else{
            return resp.result;
        }
    })
    .catch((data) => {
        loading.set(false);
        alert("Error");
    })
}

export function recoverypassword(email){
    loading.set(true);
    return fetch("/recoverypassword", {
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
        method: 'POST',
        body: JSON.stringify({
            'email': email
        })
    })
    .then(function(resp) {
        loading.set(false);
        return resp.json();
    })
    .catch((data) => {
        loading.set(false);
        alert("Error");
    })
}

export function resetPassword(password){
    loading.set(true);
    return fetch("/resetPassword", {
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
        method: 'POST',
        body: JSON.stringify({
            'password': password,
            'token': getLocationSearch()['token'],
        })
    })
    .then(function(resp) {
        loading.set(false);
        return resp.json();
    })
    .catch((data) => {
        loading.set(false);
        alert("Error");
    })
}
function getLocationSearch(){
    var search = window.location.search.substring(1);
    return JSON.parse('{"' + decodeURI(search).replace(/"/g, '\\"').replace(/&/g, '","').replace(/=/g,'":"') + '"}')
}