import { call, get_jwt_token_name } from './service.js'

function getUid(){
    let token = localStorage.getItem(get_jwt_token_name());
    let decoded = parseJWT(token);
    return decoded.id
}

function parseJWT(token){
    try {
      return JSON.parse(atob(token.split('.')[1]));
    } catch (e) {
      return null;
    }
};

export function getUserName(){
    return call("FlrUser", "get_user_name_and_company").then(
        (resp) => {
            return resp
        }
    )
}

export function logout(){
    localStorage.removeItem(get_jwt_token_name());
    window.location = window.location.pathname;
}