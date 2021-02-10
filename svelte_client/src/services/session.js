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
    let uid = getUid();
    return call("FlrUser", "read", [["name"]], {filters:[["id","=",uid]]}).then(
        (resp) => {
            return resp[0]["name"];
        }
    )
}

export function logout(){
    localStorage.clear();
    window.location = "/";
}