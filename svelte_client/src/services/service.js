import { writable } from 'svelte/store';
import { get_store_value } from 'svelte/internal';
import { globalsStore } from './writables';
import Swal from 'sweetalert2';

export const JWT_NOT_YET_LOADED = "jwt not yet loaded";
export const jwt = writable(JWT_NOT_YET_LOADED);
export const loading = writable(false);
export let appName;
export let appTitle;
export let sendErrorBtn;

fetch("/app_name")
    .then(resp => resp.text())
    .then(text => {
        appName = text;
        let tokName = get_jwt_token_name();
        if(localStorage.getItem(tokName)){
            jwt.set(localStorage.getItem(tokName));
        }else{
            jwt.set('');
        }
    })

fetch("/app_title")
    .then(resp => resp.text())
    .then(text => {
        appTitle = text;
        document.title = appTitle;
    })

fetch("/send_error_btn")
    .then(resp => resp.text())
    .then(text => {
        sendErrorBtn = text==='True';
    })

export function get_jwt_token(){
    return get_store_value(jwt);
}

export function get_jwt_token_name(){
    return `flare_${appName}_jwt`;
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
                localStorage.setItem(get_jwt_token_name(), resp.result);
            }
            loading.set(false);
            return resp;
        }
    )
}

function SweetAlert(resp){
    var style = 'overflow-y:auto;height:auto;max-height:70vh;';
    var message = resp.error.message  || 'An error has occurred';
    var html = '';
    var title = '';
    if (!resp.error.FlrException){
        style += 'text-align:left;font-family:monospace;';
        html = `<div style="${style}">${message}</div>`;
        title = 'Server Error';
    }else{
        html = `<div style="${style}">${message}</div>`;
        title = 'Warning';
    }
    Swal.fire({
        title: title,
        html: html.replace(/\n/g,"<br/>"),
        width: '70%',
        buttonsStyling: false,
        customClass: {
            confirmButton: "btn btn-danger"
        },
        confirmButtonText: 'Send to administrator',
        showConfirmButton: sendErrorBtn,
        showCloseButton: true
      }).then((result) => {
        /* Read more about isConfirmed, isDenied below */
        if (result.isConfirmed) {
            if (sendError(resp.error)){
                Swal.fire({
                    icon: "success",
                    text: 'Error was send to administrator',
                    timer: 4000,
                    showConfirmButton: false,
                    showCloseButton: true,
                })
            }
        }
    })

}

function sendError(error){
    loading.set(true);
    return fetch('/send_error', {
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify({
            data: error.data
        })
    })
    .then(function(resp) {
        if(resp.error){
            SweetAlert(resp);
        }else{
            return resp.json();
        }
    }).catch((data) => {
        loading.set(false);
    })
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
            SweetAlert(resp)
            resp.$error = resp.error;
            return resp;
        }else{
            return resp.result;
        }
    })
    .catch((data) => {
        loading.set(false);
    })
}

export function importData(model, fields, file) {
    loading.set(true);
    const data = new FormData();
    data.append("file", file);
    data.append("model", model);
    data.append("fields", fields);
    data.append("token", get_store_value(jwt))

    return fetch("/flrimport", {
        method: "POST",
        body: data,
    }).then(async function(_resp) {
        loading.set(false);
        var resp = await _resp.json();
        if(resp.error){
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