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