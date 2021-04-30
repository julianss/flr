export function getUniqueId() {
    return Date.now().toString() + "-" + Math.random().toString().substring(2);
}

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

function padZero(n,zeros) {
    n = n.toString();
    return n.padStart(zeros, "0");
}

//Convert datetime string from UTC to local or from local to UTC
//Source string must be in ISO format the format (YYYY-MM-DDTHH:MM:SS)
//When converting from UTC to local, the output can be a locale string or a ISO format string
function convertDateTime(dateString, from, localeString) {
    if(!dateString){
        return '';
    }
    dateString = dateString.replace(" ", "T");
    dateString = dateString.replace("Z", "");
    if(dateString.length == 16){
        dateString += ":00";
    }
    var splitted = dateString.split("T");
    var datePart = splitted[0];
    var timePart = splitted[1];
    var splittedDatePart = datePart.split("-");
    var splittedTimePart = timePart.split(":");
    var year = parseInt(splittedDatePart[0]);
    var month = parseInt(splittedDatePart[1] - 1);
    var day = parseInt(splittedDatePart[2]);
    var hour = parseInt(splittedTimePart[0]);
    var minute = parseInt(splittedTimePart[1]);
    var second = parseInt(splittedTimePart[2]);
    if(from == "UTC"){
        var d = new Date(Date.UTC(year, month, day, hour, minute, second));
        if(localeString){
            return d.toLocaleString();
        }else{
            var isoLocal = `${d.getFullYear()}-${padZero(d.getMonth()+1,2)}-${padZero(d.getDate(),2)}`;
            isoLocal += "T";
            isoLocal += `${padZero(d.getHours(),2)}:${padZero(d.getMinutes(),2)}:${padZero(d.getSeconds(),2)}`;
            console.log(dateString, "converted to", isoLocal);
            return isoLocal;
        }
    }else if(from == "local"){
        var d = new Date(year, month, day, hour, minute, second);
        var utc = d.toISOString();
        return utc.substring(0, 19);
    }
}

//UTC to local, resulting string is human friendly
export function renderDateTime(dateString){
    return convertDateTime(dateString, "UTC", true);
}

//UTC to local, maintains ISO format
export function UTCtoLocal(dateString) {
    return convertDateTime(dateString, "UTC");
}

//Local to UTC, mantains ISO format
export function localToUTC(dateString) {
    return convertDateTime(dateString, "local");
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