export function renderDate(dateString) {
    if(!dateString){
        return '';
    }
    var splitted = dateString.split("-");
    var year = parseInt(splitted[0]);
    var month = parseInt(splitted[1] - 1);
    var day = parseInt(splitted[2]);
    var d = new Date(year, month, day);
    return d.toLocaleDateString();
}

export function parseHash(){
    var hash = window.location.hash.substring(1);
    var params = {}
    hash.split('&').map(hk => { 
        let temp = hk.split('='); 
        params[temp[0]] = temp[1] 
    });
    return params;
}

export function objectToHashString(obj){
    var pairs = [];
    for(var k in obj){
        var v = obj[k];
        pairs.push(`${k}=${v}`);
    }
    return "#" + pairs.join("&");
}

export function replaceHash(obj){
    var hash = objectToHashString(obj);
    history.pushState(null, null, hash);
}

export function updateHash(obj){
    var params = parseHash();
    for(var k in obj){
        params[k] = obj[k];
    }
    var newParams = {};
    for(var k in params){
        if(params[k] !== null){
            newParams[k] = params[k];
        }
    }
    var hash = objectToHashString(newParams);
    history.pushState(null, null, hash);
}